"""Recommendation Agent."""

from __future__ import annotations

from app.models import RecommendationResponse, UserInput
from app.utils.helpers import build_explanation, load_policies
from app.agents.policy_evaluation import PolicyEvaluationAgent
from app.agents.risk_analysis import RiskAnalysisAgent
from app.agents.user_profiling import UserProfilingAgent


class RecommendationAgent:
    """Coordinate the end-to-end recommendation flow."""

    def __init__(self) -> None:
        self.user_profiler = UserProfilingAgent()
        self.risk_analyzer = RiskAnalysisAgent()
        self.policy_evaluator = PolicyEvaluationAgent()

    def recommend(self, user_input: UserInput) -> RecommendationResponse:
        """Run the MVP pipeline and return a recommendation response."""
        profile = self.user_profiler.build_profile(user_input)
        risk_score, risk_label = self.risk_analyzer.calculate_risk(profile)
        policies = load_policies()
        ranked = self.policy_evaluator.rank_policies(profile, policies, risk_score, risk_label)
        best_policy = ranked[0]

        explanation = build_explanation(
            best_policy.policy.policy_name,
            risk_label,
            [
                f"The policy scored strongly on suitability, especially for {profile.insurance_goal}.",
                f"Its premium of {best_policy.policy.premium:.0f} stays balanced against the user's affordability band.",
                f"The coverage of {best_policy.policy.coverage:.0f} supports the user's current protection need.",
            ]
            + best_policy.explanation_points,
        )

        return RecommendationResponse(
            user_profile=profile,
            risk_score=risk_score,
            risk_label=risk_label,
            best_policy=best_policy,
            top_policies=ranked[:3],
            explanation=explanation,
        )
