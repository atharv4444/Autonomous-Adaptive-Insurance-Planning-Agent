"""Core tests for the insurance planning prototype."""

from app.agents.recommendation import RecommendationAgent
from app.models import UserInput


def test_recommendation_returns_top_three() -> None:
    agent = RecommendationAgent()
    result = agent.recommend(
        UserInput(
            age=35,
            income=900000,
            dependents=2,
            assets=2000000,
            liabilities=1500000,
            insurance_goal="family_protection",
        )
    )

    assert result.best_policy.policy.policy_name
    assert len(result.top_policies) == 3
    assert result.risk_score > 0
    assert "recommended because" in result.explanation


def test_high_liability_user_has_non_low_risk() -> None:
    agent = RecommendationAgent()
    result = agent.recommend(
        UserInput(
            age=42,
            income=400000,
            dependents=3,
            assets=100000,
            liabilities=900000,
            insurance_goal="family_protection",
        )
    )

    assert result.risk_label in {"moderate", "high"}
    assert result.best_policy.total_score >= result.top_policies[-1].total_score
