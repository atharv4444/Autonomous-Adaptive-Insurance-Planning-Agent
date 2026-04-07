"""Recommendation Agent."""

from __future__ import annotations

from app.agents.critic import CriticAgent
from app.agents.policy_evaluation import PolicyEvaluationAgent
from app.agents.scenario_simulation import ScenarioSimulationAgent
from app.agents.risk_analysis import RiskAnalysisAgent
from app.agents.user_profiling import UserProfilingAgent
from app.memory.memory_store import MemoryStore
from app.models import MemorySnapshot, RankedPolicy, RecommendationResponse, UserInput
from app.utils.helpers import load_policies


class RecommendationAgent:
    """Coordinate the end-to-end recommendation flow."""

    def __init__(self) -> None:
        self.user_profiler = UserProfilingAgent()
        self.risk_analyzer = RiskAnalysisAgent()
        self.scenario_simulator = ScenarioSimulationAgent()
        self.policy_evaluator = PolicyEvaluationAgent()
        self.critic = CriticAgent()
        self.memory_store = MemoryStore()

    def recommend(self, user_input: UserInput) -> RecommendationResponse:
        """Run the MVP pipeline and return a recommendation response."""
        profile = self.user_profiler.build_profile(user_input)
        risk_score, risk_label = self.risk_analyzer.calculate_risk(profile)
        scenario_result = self.scenario_simulator.simulate()
        policies = load_policies()
        ranked = self.policy_evaluator.rank_policies(
            profile,
            policies,
            risk_score,
            risk_label,
            scenario_result.expected_loss,
        )
        critic_result = self.critic.validate(
            ranked_policies=ranked,
            profile=profile,
            risk_label=risk_label,
            expected_loss=scenario_result.expected_loss,
        )
        best_policy = critic_result.validated_policy
        profile_signature = self.memory_store.save_user_profile(profile)
        self.memory_store.save_recommendation(profile_signature, best_policy)
        memory_snapshot = MemorySnapshot(
            profile_signature=profile_signature,
            previous_recommendations=self.memory_store.get_previous_recommendations(limit=3),
        )

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
