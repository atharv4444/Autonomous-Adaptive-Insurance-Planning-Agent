"""Recommendation Agent — orchestrates the full multi-agent pipeline.

When Gemini is available, uses a ReAct (Reason + Act) loop to let the LLM
decide which tool to call next.  Falls back to the original fixed 6-step
pipeline when the LLM is unavailable.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

from app.agents.critic import CriticAgent
from app.agents.policy_evaluation import PolicyEvaluationAgent
from app.agents.scenario_simulation import ScenarioSimulationAgent
from app.agents.risk_analysis import RiskAnalysisAgent
from app.agents.user_profiling import UserProfilingAgent
from app.memory.memory_store import MemoryStore
from app.models import (
    AgentTraceEntry,
    MemorySnapshot,
    RankedPolicy,
    RecommendationResponse,
    UserInput,
    UserProfile,
)
from app.utils.helpers import load_policies
import app.llm.client as llm
from app.llm.prompts import (
    ORCHESTRATION_SYSTEM_PROMPT,
    explanation_prompt,
)

logger = logging.getLogger(__name__)

# Maximum ReAct iterations (safety cap)
_MAX_REACT_STEPS = 10


class RecommendationAgent:
    """Coordinate the end-to-end recommendation flow with inter-agent tracing."""

    def __init__(self) -> None:
        self.user_profiler = UserProfilingAgent()
        self.risk_analyzer = RiskAnalysisAgent()
        self.scenario_simulator = ScenarioSimulationAgent()
        self.policy_evaluator = PolicyEvaluationAgent()
        self.critic = CriticAgent()
        self.memory_store = MemoryStore()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def recommend(self, user_input: UserInput) -> RecommendationResponse:
        """Run the full multi-agent pipeline and return a traced recommendation."""
        if llm.is_available():
            try:
                return self._react_pipeline(user_input)
            except Exception as exc:
                logger.error("ReAct pipeline failed, falling back to fixed pipeline: %s", exc)
        return self._fixed_pipeline(user_input)

    # ------------------------------------------------------------------
    # ReAct (LLM-driven) orchestration loop
    # ------------------------------------------------------------------
    def _react_pipeline(self, user_input: UserInput) -> RecommendationResponse:
        """LLM decides which tool to call next at each step."""
        trace: List[AgentTraceEntry] = []

        # Shared state accumulated across tool calls
        state: Dict[str, Any] = {"user_input": user_input}
        completed_tools: List[str] = []

        # Build initial context message
        context = (
            ORCHESTRATION_SYSTEM_PROMPT
            + f"\n\nUSER INPUT:\n{json.dumps(user_input.model_dump(), indent=2)}"
            + "\n\nBegin orchestration. Respond with your first action."
        )

        for step in range(_MAX_REACT_STEPS):
            llm_response = llm.chat_json(context)
            if not llm_response or "action" not in llm_response:
                logger.warning("ReAct step %d: unreadable LLM response, breaking loop.", step)
                break

            action = llm_response.get("action", "")
            thought = llm_response.get("thought", "")
            logger.info("ReAct step %d | action=%s | thought=%s", step, action, thought)

            if action == "finish":
                break

            tool_result, duration_ms = self._execute_tool(action, state)
            completed_tools.append(action)

            trace.append(AgentTraceEntry(
                agent_name=f"ReAct[{action}]",
                input_summary=thought,
                output_summary=str(tool_result)[:200],
                duration_ms=round(duration_ms, 2),
            ))

            # Feed tool result back into context for next LLM step
            context += (
                f"\n\nACTION RESULT for '{action}':\n{json.dumps(tool_result, indent=2, default=str)}"
                f"\n\nCompleted actions: {completed_tools}"
                f"\nRemaining budget: {_MAX_REACT_STEPS - step - 1} steps. What is your next action?"
            )

        # If any required tools weren't called, run them now
        self._ensure_required_tools(state)

        return self._build_response(state, trace, user_input)

    def _execute_tool(self, action: str, state: Dict[str, Any]) -> tuple[Any, float]:
        """Execute a named tool and store results in shared state. Returns (result, duration_ms)."""
        t0 = time.perf_counter()
        result: Any = {"status": "unknown_tool", "action": action}

        if action == "build_user_profile":
            profile = self.user_profiler.build_profile(state["user_input"])
            state["profile"] = profile
            result = profile.model_dump()

        elif action == "calculate_risk":
            profile: UserProfile = state.get("profile") or self.user_profiler.build_profile(state["user_input"])
            state["profile"] = profile
            risk_score, risk_label = self.risk_analyzer.calculate_risk(profile)
            state["risk_score"] = risk_score
            state["risk_label"] = risk_label
            result = {"risk_score": risk_score, "risk_label": risk_label}

        elif action == "simulate_scenarios":
            profile = state.get("profile") or self.user_profiler.build_profile(state["user_input"])
            state["profile"] = profile
            scenario_result = self.scenario_simulator.simulate(profile)
            state["scenario_result"] = scenario_result
            result = {
                "expected_loss": scenario_result.expected_loss,
                "scenarios": [s.scenario_name for s in scenario_result.scenario_breakdown],
            }

        elif action == "rank_policies":
            profile = state.get("profile") or self.user_profiler.build_profile(state["user_input"])
            risk_score = state.get("risk_score", 50.0)
            risk_label = state.get("risk_label", "moderate")
            expected_loss_obj = state.get("scenario_result", None)
            expected_loss = expected_loss_obj.expected_loss if expected_loss_obj else 0.0
            policies = load_policies()
            ranked = self.policy_evaluator.rank_policies(profile, policies, risk_score, risk_label, expected_loss)
            state["ranked"] = ranked
            result = {"top_3": [r.policy.policy_name for r in ranked[:3]]}

        elif action == "validate_recommendation":
            profile = state.get("profile") or self.user_profiler.build_profile(state["user_input"])
            ranked: List[RankedPolicy] = state.get("ranked", [])
            risk_label = state.get("risk_label", "moderate")
            expected_loss_obj = state.get("scenario_result", None)
            expected_loss = expected_loss_obj.expected_loss if expected_loss_obj else 0.0
            if not ranked:
                policies = load_policies()
                risk_score = state.get("risk_score", 50.0)
                ranked = self.policy_evaluator.rank_policies(profile, policies, risk_score, risk_label, expected_loss)
                state["ranked"] = ranked
            critic_result = self.critic.validate(ranked, profile, risk_label, expected_loss)
            state["critic_result"] = critic_result
            result = {
                "validated_policy": critic_result.validated_policy.policy.policy_name,
                "confidence_score": critic_result.confidence_score,
                "issues": critic_result.issues,
            }

        duration_ms = (time.perf_counter() - t0) * 1000
        return result, duration_ms

    def _ensure_required_tools(self, state: Dict[str, Any]) -> None:
        """Run any required tools that the LLM may have skipped."""
        user_input: UserInput = state["user_input"]
        if "profile" not in state:
            state["profile"] = self.user_profiler.build_profile(user_input)
        if "risk_score" not in state:
            state["risk_score"], state["risk_label"] = self.risk_analyzer.calculate_risk(state["profile"])
        if "scenario_result" not in state:
            state["scenario_result"] = self.scenario_simulator.simulate(state["profile"])
        if "ranked" not in state:
            policies = load_policies()
            state["ranked"] = self.policy_evaluator.rank_policies(
                state["profile"], policies,
                state["risk_score"], state.get("risk_label", "moderate"),
                state["scenario_result"].expected_loss,
            )
        if "critic_result" not in state:
            state["critic_result"] = self.critic.validate(
                state["ranked"], state["profile"],
                state.get("risk_label", "moderate"),
                state["scenario_result"].expected_loss,
            )

    # ------------------------------------------------------------------
    # Original fixed 6-step pipeline (fallback)
    # ------------------------------------------------------------------
    def _fixed_pipeline(self, user_input: UserInput) -> RecommendationResponse:
        """Original hard-coded pipeline, used when LLM is unavailable."""
        trace: List[AgentTraceEntry] = []

        t0 = time.perf_counter()
        profile = self.user_profiler.build_profile(user_input)
        trace.append(AgentTraceEntry(
            agent_name="UserProfilingAgent",
            input_summary=f"age={user_input.age}, income={user_input.income}",
            output_summary=f"life_stage={profile.life_stage}, net_worth={profile.net_worth:.0f}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        t0 = time.perf_counter()
        risk_score, risk_label = self.risk_analyzer.calculate_risk(profile)
        trace.append(AgentTraceEntry(
            agent_name="RiskAnalysisAgent",
            input_summary=f"age={profile.age}, income={profile.income}",
            output_summary=f"risk_score={risk_score}, risk_label={risk_label}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        t0 = time.perf_counter()
        scenario_result = self.scenario_simulator.simulate(profile)
        trace.append(AgentTraceEntry(
            agent_name="ScenarioSimulationAgent",
            input_summary=f"age={profile.age}, liabilities={profile.liabilities}",
            output_summary=f"expected_loss={scenario_result.expected_loss:.0f}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        t0 = time.perf_counter()
        policies = load_policies()
        ranked = self.policy_evaluator.rank_policies(profile, policies, risk_score, risk_label, scenario_result.expected_loss)
        trace.append(AgentTraceEntry(
            agent_name="PolicyEvaluationAgent",
            input_summary=f"{len(policies)} policies, risk={risk_label}",
            output_summary=f"top_3={[rp.policy.policy_name for rp in ranked[:3]]}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        t0 = time.perf_counter()
        critic_result = self.critic.validate(ranked, profile, risk_label, scenario_result.expected_loss)
        trace.append(AgentTraceEntry(
            agent_name="CriticAgent",
            input_summary=f"top_3_policies, risk={risk_label}",
            output_summary=f"validated={critic_result.validated_policy.policy.policy_name}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        t0 = time.perf_counter()
        profile_signature = self.memory_store.save_user_profile(profile)
        self.memory_store.save_recommendation(profile_signature, critic_result.validated_policy)
        memory_snapshot = MemorySnapshot(
            profile_signature=profile_signature,
            previous_recommendations=self.memory_store.get_previous_recommendations(limit=3),
        )
        trace.append(AgentTraceEntry(
            agent_name="MemoryStore",
            input_summary=f"profile_signature={profile_signature}",
            output_summary=f"saved, history_count={len(memory_snapshot.previous_recommendations)}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        state = {
            "profile": profile,
            "risk_score": risk_score,
            "risk_label": risk_label,
            "scenario_result": scenario_result,
            "ranked": ranked,
            "critic_result": critic_result,
            "memory_snapshot": memory_snapshot,
        }
        return self._build_response(state, trace, user_input)

    # ------------------------------------------------------------------
    # Response builder (shared by both pipelines)
    # ------------------------------------------------------------------
    def _build_response(
        self,
        state: Dict[str, Any],
        trace: List[AgentTraceEntry],
        user_input: UserInput,
    ) -> RecommendationResponse:
        profile = state["profile"]
        risk_score = state["risk_score"]
        risk_label = state["risk_label"]
        scenario_result = state["scenario_result"]
        ranked: List[RankedPolicy] = state["ranked"]
        critic_result = state["critic_result"]
        best_policy = critic_result.validated_policy

        # Memory
        if "memory_snapshot" not in state:
            profile_signature = self.memory_store.save_user_profile(profile)
            self.memory_store.save_recommendation(profile_signature, best_policy)
            memory_snapshot = MemorySnapshot(
                profile_signature=profile_signature,
                previous_recommendations=self.memory_store.get_previous_recommendations(limit=3),
            )
        else:
            memory_snapshot = state["memory_snapshot"]

        explanation = self._build_explanation(
            best_policy=best_policy,
            risk_label=risk_label,
            risk_score=risk_score,
            expected_loss=scenario_result.expected_loss,
            critic_issues=critic_result.issues,
            profile=profile,
        )

        return RecommendationResponse(
            user_profile=profile,
            risk_score=risk_score,
            risk_label=risk_label,
            expected_loss=scenario_result.expected_loss,
            scenario_breakdown=scenario_result.scenario_breakdown,
            best_policy=best_policy,
            final_recommendation=best_policy,
            top_policies=ranked[:3],
            critic_issues=critic_result.issues,
            confidence_score=critic_result.confidence_score,
            memory_snapshot=memory_snapshot,
            explanation=explanation,
            agent_trace=trace,
        )

    # ------------------------------------------------------------------
    # Explanation builder
    # ------------------------------------------------------------------
    def _build_explanation(
        self,
        best_policy: RankedPolicy,
        risk_label: str,
        risk_score: float,
        expected_loss: float,
        critic_issues: List[str],
        profile: Optional[UserProfile] = None,
    ) -> str:
        critic_summary = next(
            (i for i in critic_issues if i.startswith("AI Critique:")),
            critic_issues[0] if critic_issues else "No major issues found.",
        )

        if llm.is_available() and profile is not None:
            prompt = explanation_prompt(
                user_name="the client",
                profile_json=json.dumps({
                    "age": profile.age,
                    "income": profile.income,
                    "dependents": profile.dependents,
                    "life_stage": profile.life_stage,
                    "insurance_goal": profile.insurance_goal,
                    "net_worth": profile.net_worth,
                }, indent=2),
                risk_label=risk_label,
                risk_score=risk_score,
                expected_loss=expected_loss,
                policy_name=best_policy.policy.policy_name,
                premium=best_policy.policy.premium,
                coverage=best_policy.policy.coverage,
                critic_summary=critic_summary,
            )
            llm_text = llm.chat(prompt, temperature=0.4)
            if llm_text:
                return llm_text

        # Fallback to template
        return (
            f"{best_policy.policy.policy_name} is recommended because it balances high coverage "
            f"with an acceptable premium for a {risk_label} risk profile. "
            f"The scenario simulation estimated an expected loss of {expected_loss:.0f}, "
            f"which was included in the utility-based ranking. "
            f"Its premium-to-income ratio is {best_policy.premium_ratio:.2%} and the tradeoff "
            f"remains favorable because {best_policy.tradeoff_summary} "
            f"Critic review: {critic_summary}"
        )
