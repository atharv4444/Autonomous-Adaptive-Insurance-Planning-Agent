"""Goal-based Planner Agent — formalizes orchestration as a goal-directed search for the best policy."""

from __future__ import annotations

import os
import time
from typing import List, Optional

from app.agents.critic import CriticAgent
from app.agents.policy_evaluation import PolicyEvaluationAgent
from app.agents.risk_analysis import RiskAnalysisAgent
from app.agents.scenario_simulation import ScenarioSimulationAgent
from app.agents.user_profiling import UserProfilingAgent
from app.memory.memory_store import MemoryStore
from app.models import (
    AgentTraceEntry,
    RankedPolicy,
    RecommendationResponse,
    UserInput,
    MemorySnapshot,
)
from app.utils.helpers import load_policies
from app.utils.regulatory import IRDAI_REGULATORY_NOTE
from app.llm.gemini_explainer import generate_explanation_with_gemini, gemini_key_present


class GoalPlannerAgent:
    """
    A goal-based agent that coordinates all sub-agents to achieve the primary goal:
    'Find and validate the most suitable insurance policy for the customer.'

    It orchestrates the decision-making process by:
    1. Parsing the goal into a structured plan.
    2. Executing the plan through specialized agents.
    3. Validating if the outcome meets the suitability criteria.
    """

    def __init__(self) -> None:
        # Initialize the knowledge of its subordinates
        self.user_profiler = UserProfilingAgent()
        self.risk_analyzer = RiskAnalysisAgent()
        self.scenario_simulator = ScenarioSimulationAgent()
        self.policy_evaluator = PolicyEvaluationAgent()
        self.critic = CriticAgent()
        self.memory_store = MemoryStore()

        # The primary goal definition
        self.primary_goal = "Find the most suitable policy available for the customer"

    def execute_plan(self, user_input: UserInput) -> RecommendationResponse:
        """
        Orchestrates the multi-agent flow with a goal-centric approach.
        """
        trace: List[AgentTraceEntry] = []

        # ── Step 1: Understand the User (Building World Model) ──
        t0 = time.perf_counter()
        profile = self.user_profiler.build_profile(user_input)
        trace.append(self._create_trace("UserProfilingAgent", t0, 
            f"Goal: Structure user data for {user_input.insurance_goal}",
            f"Result: Profile created for life_stage={profile.life_stage}"))

        # ── Step 2: Assess Environment Risk ──
        t0 = time.perf_counter()
        risk_score, risk_label = self.risk_analyzer.calculate_risk(profile)
        trace.append(self._create_trace("RiskAnalysisAgent", t0,
            "Goal: Determine transparent financial risk score",
            f"Result: risk_score={risk_score} ({risk_label})"))

        # ── Step 3: Predictive Simulation (Potential States) ──
        t0 = time.perf_counter()
        scenario_result = self.scenario_simulator.simulate(profile)
        trace.append(self._create_trace("ScenarioSimulationAgent", t0,
            "Goal: Simulate future loss scenarios to inform utility",
            f"Result: expected_loss={scenario_result.expected_loss:.0f}"))

        # ── Step 4: Policy Search & Selection (Evaluating Options) ──
        t0 = time.perf_counter()
        policies = load_policies()
        ranked = self.policy_evaluator.rank_policies(
            profile, policies, risk_score, risk_label, scenario_result.expected_loss
        )
        trace.append(self._create_trace("PolicyEvaluationAgent", t0,
            "Goal: Search and rank policies by utility and fit",
            f"Result: Identified {len(ranked)} candidates, top match: {ranked[0].policy.policy_name}"))

        # ── Step 5: Critique & Validation (Ensuring Goal Alignment) ──
        t0 = time.perf_counter()
        critic_result = self.critic.validate(
            ranked_policies=ranked,
            profile=profile,
            risk_label=risk_label,
            expected_loss=scenario_result.expected_loss,
        )
        best_policy = critic_result.validated_policy
        trace.append(self._create_trace("CriticAgent", t0,
            "Goal: Validate top candidate for coverage gaps or issues",
            f"Result: Validated {best_policy.policy.policy_name} with {critic_result.confidence_score}% confidence"))

        # ── Step 6: Memory Integration (Learning from State) ──
        t0 = time.perf_counter()
        profile_signature = self.memory_store.save_user_profile(profile)
        self.memory_store.save_recommendation(profile_signature, best_policy)
        memory_snapshot = MemorySnapshot(
            profile_signature=profile_signature,
            previous_recommendations=self.memory_store.get_previous_recommendations(limit=3),
        )
        trace.append(self._create_trace("MemoryStore", t0,
            "Goal: Persist decision for future context",
            f"Result: Session saved (history_count={len(memory_snapshot.previous_recommendations)})"))

        # ── Step 7: Goal Accomplished - Finalize Explanation ──
        explanation = self._build_explanation(
            best_policy=best_policy,
            risk_label=risk_label,
            expected_loss=scenario_result.expected_loss,
            critic_issues=critic_result.issues,
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
            regulatory_note=IRDAI_REGULATORY_NOTE,
            agent_trace=trace,
        )

    def _build_explanation(
        self,
        best_policy: RankedPolicy,
        risk_label: str,
        expected_loss: float,
        critic_issues: list[str],
    ) -> str:
        """Create a richer multi-agent explanation for the final recommendation."""
        critic_summary = critic_issues[0] if critic_issues else "The critic found no major issues."

        template = (
            f"{best_policy.policy.policy_name} is recommended because it balances high coverage with an acceptable premium "
            f"for a {risk_label} risk profile. "
            f"The scenario simulation estimated an expected loss of {expected_loss:.0f}, which was included in the utility-based ranking. "
            f"Its premium-to-income ratio is {best_policy.premium_ratio:.2%} and the tradeoff remains favorable because {best_policy.tradeoff_summary} "
            f"Critic review: {critic_summary}"
        )

        if not gemini_key_present():
            return template

        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        prompt = (
            "You are an insurance planning assistant. Write a concise, user-friendly explanation (2-5 sentences) "
            "for why the recommended policy was chosen. Avoid disclaimers. Don't mention internal agent names. "
            "Use INR currency symbol ₹ where relevant.\n\n"
            f"Recommended policy: {best_policy.policy.policy_name}\n"
            f"Policy type: {best_policy.policy.policy_type}\n"
            f"Coverage: ₹{best_policy.policy.coverage:,.0f}\n"
            f"Annual premium: ₹{best_policy.policy.premium:,.0f}\n"
            f"Premium-to-income ratio: {best_policy.premium_ratio:.2%}\n"
            f"Coverage gap: ₹{best_policy.coverage_gap:,.0f}\n"
            f"Risk label: {risk_label}\n"
            f"Expected loss (simulated): ₹{expected_loss:,.0f}\n"
            f"Tradeoff summary: {best_policy.tradeoff_summary}\n"
            f"Critic note: {critic_summary}\n"
        )

        llm_text = generate_explanation_with_gemini(prompt=prompt, model=model)
        return llm_text or template

    def _create_trace(self, name: str, start_time: float, input_txt: str, output_txt: str) -> AgentTraceEntry:
        return AgentTraceEntry(
            agent_name=name,
            input_summary=input_txt,
            output_summary=output_txt,
            duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
        )
