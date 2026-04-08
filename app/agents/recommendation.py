"""Recommendation Agent — orchestrates the full multi-agent pipeline with tracing."""

from __future__ import annotations

import time
from typing import List

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
)
from app.utils.helpers import load_policies


class RecommendationAgent:
    """Coordinate the end-to-end recommendation flow with inter-agent tracing."""

    def __init__(self) -> None:
        self.user_profiler = UserProfilingAgent()
        self.risk_analyzer = RiskAnalysisAgent()
        self.scenario_simulator = ScenarioSimulationAgent()
        self.policy_evaluator = PolicyEvaluationAgent()
        self.critic = CriticAgent()
        self.memory_store = MemoryStore()

    def recommend(self, user_input: UserInput) -> RecommendationResponse:
        """Run the full multi-agent pipeline and return a traced recommendation."""
        trace: List[AgentTraceEntry] = []

        # ── Step 1: User Profiling Agent ──
        t0 = time.perf_counter()
        profile = self.user_profiler.build_profile(user_input)
        trace.append(AgentTraceEntry(
            agent_name="UserProfilingAgent",
            input_summary=f"age={user_input.age}, income={user_input.income}, dependents={user_input.dependents}, goal={user_input.insurance_goal}",
            output_summary=f"life_stage={profile.life_stage}, affordability={profile.affordability_band}, net_worth={profile.net_worth:.0f}, liability_ratio={profile.liability_ratio}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        # ── Step 2: Risk Analysis Agent ──
        t0 = time.perf_counter()
        risk_score, risk_label = self.risk_analyzer.calculate_risk(profile)
        trace.append(AgentTraceEntry(
            agent_name="RiskAnalysisAgent",
            input_summary=f"profile(age={profile.age}, income={profile.income}, dependents={profile.dependents})",
            output_summary=f"risk_score={risk_score}, risk_label={risk_label}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        # ── Step 3: Scenario Simulation Agent ──
        t0 = time.perf_counter()
        scenario_result = self.scenario_simulator.simulate(profile)
        scenario_names = [s.scenario_name for s in scenario_result.scenario_breakdown]
        trace.append(AgentTraceEntry(
            agent_name="ScenarioSimulationAgent",
            input_summary=f"profile(age={profile.age}, income={profile.income}, liabilities={profile.liabilities})",
            output_summary=f"expected_loss={scenario_result.expected_loss:.0f}, scenarios={scenario_names}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        # ── Step 4: Policy Evaluation Agent ──
        t0 = time.perf_counter()
        policies = load_policies()
        ranked = self.policy_evaluator.rank_policies(
            profile,
            policies,
            risk_score,
            risk_label,
            scenario_result.expected_loss,
        )
        top_names = [rp.policy.policy_name for rp in ranked[:3]]
        trace.append(AgentTraceEntry(
            agent_name="PolicyEvaluationAgent",
            input_summary=f"{len(policies)} policies, risk={risk_label}, expected_loss={scenario_result.expected_loss:.0f}",
            output_summary=f"ranked {len(ranked)} policies, top_3={top_names}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        # ── Step 5: Critic Agent ──
        t0 = time.perf_counter()
        critic_result = self.critic.validate(
            ranked_policies=ranked,
            profile=profile,
            risk_label=risk_label,
            expected_loss=scenario_result.expected_loss,
        )
        best_policy = critic_result.validated_policy
        trace.append(AgentTraceEntry(
            agent_name="CriticAgent",
            input_summary=f"top_3_policies, risk={risk_label}, expected_loss={scenario_result.expected_loss:.0f}",
            output_summary=f"validated={best_policy.policy.policy_name}, confidence={critic_result.confidence_score}, issues={len(critic_result.issues)}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

        # ── Step 6: Memory Store ──
        t0 = time.perf_counter()
        profile_signature = self.memory_store.save_user_profile(profile)
        self.memory_store.save_recommendation(profile_signature, best_policy)
        memory_snapshot = MemorySnapshot(
            profile_signature=profile_signature,
            previous_recommendations=self.memory_store.get_previous_recommendations(limit=3),
        )
        trace.append(AgentTraceEntry(
            agent_name="MemoryStore",
            input_summary=f"profile_signature={profile_signature}",
            output_summary=f"saved profile + recommendation, history_count={len(memory_snapshot.previous_recommendations)}",
            duration_ms=round((time.perf_counter() - t0) * 1000, 2),
        ))

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
        # TODO: Replace template explanations with LLM-generated rationale when available.
        # TODO: Add advanced ML-based recommendation blending once more training data exists.
        return (
            f"{best_policy.policy.policy_name} is recommended because it balances high coverage with an acceptable premium "
            f"for a {risk_label} risk profile. "
            f"The scenario simulation estimated an expected loss of {expected_loss:.0f}, which was included in the utility-based ranking. "
            f"Its premium-to-income ratio is {best_policy.premium_ratio:.2%} and the tradeoff remains favorable because {best_policy.tradeoff_summary} "
            f"Critic review: {critic_summary}"
        )
