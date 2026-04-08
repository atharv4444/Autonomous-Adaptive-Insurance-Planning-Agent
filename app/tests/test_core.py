"""Core tests for the insurance planning prototype."""

from pathlib import Path

from app.agents.critic import CriticAgent
from app.agents.policy_evaluation import PolicyEvaluationAgent
from app.agents.recommendation import RecommendationAgent
from app.agents.scenario_simulation import ScenarioSimulationAgent
from app.agents.user_profiling import UserProfilingAgent
from app.memory.memory_store import MemoryStore
from app.models import Policy, RankedPolicy, UserInput, UserProfile
from app.utils.helpers import load_policies


def _build_sample_profile(**overrides: object) -> UserProfile:
    """Helper to create a UserProfile with sensible defaults and optional overrides."""
    defaults = {
        "age": 35,
        "income": 900000,
        "dependents": 2,
        "assets": 2000000,
        "liabilities": 1500000,
        "insurance_goal": "family_protection",
        "net_worth": 500000,
        "affordability_band": "medium",
        "life_stage": "family_builder",
        "liability_ratio": 1.67,
    }
    defaults.update(overrides)
    return UserProfile(**defaults)


def test_scenario_simulation_returns_expected_loss() -> None:
    """Static fallback still works when no profile is passed."""
    result = ScenarioSimulationAgent().simulate()

    assert result.expected_loss == 16000.0
    assert len(result.scenario_breakdown) == 3


def test_scenario_simulation_with_profile_varies_by_age() -> None:
    """A 55-year-old should have higher expected loss than a 25-year-old."""
    young_profile = _build_sample_profile(age=25, life_stage="early_career")
    old_profile = _build_sample_profile(age=55, life_stage="pre_retirement")

    young_result = ScenarioSimulationAgent().simulate(young_profile)
    old_result = ScenarioSimulationAgent().simulate(old_profile)

    assert old_result.expected_loss > young_result.expected_loss
    assert len(old_result.scenario_breakdown) == 3


def test_scenario_simulation_with_dependents_increases_cost() -> None:
    """More dependents should increase expected loss."""
    no_dep = _build_sample_profile(dependents=0)
    many_dep = _build_sample_profile(dependents=4)

    no_dep_result = ScenarioSimulationAgent().simulate(no_dep)
    many_dep_result = ScenarioSimulationAgent().simulate(many_dep)

    assert many_dep_result.expected_loss > no_dep_result.expected_loss


def test_scenario_simulation_with_high_liabilities() -> None:
    """High liability ratio should increase income loss probability."""
    low_liability = _build_sample_profile(liabilities=0, liability_ratio=0.0, net_worth=2000000)
    high_liability = _build_sample_profile(liabilities=3000000, liability_ratio=3.33, net_worth=-1000000)

    low_result = ScenarioSimulationAgent().simulate(low_liability)
    high_result = ScenarioSimulationAgent().simulate(high_liability)

    # Find income_loss scenario in both
    low_income_loss = next(s for s in low_result.scenario_breakdown if s.scenario_name == "income_loss")
    high_income_loss = next(s for s in high_result.scenario_breakdown if s.scenario_name == "income_loss")

    assert high_income_loss.probability > low_income_loss.probability


def test_memory_store_saves_and_loads_recommendations(tmp_path: Path) -> None:
    store = MemoryStore(storage_path=tmp_path / "memory.json")
    profile = _build_sample_profile()
    ranked_policy = RankedPolicy(
        policy=Policy(
            policy_name="Test Policy",
            policy_type="term_life",
            coverage=5000000,
            premium=25000,
            target_profile=["family_protection", "family_builder", "high"],
            notes="Test policy",
        ),
        total_score=90.0,
        suitability_score=92.0,
        affordability_score=85.0,
        coverage_score=88.0,
        utility_score=80.0,
        premium_ratio=0.03,
        coverage_gap=1000000.0,
        tradeoff_summary="Good balance for testing.",
        explanation_points=["Strong fit."],
    )

    signature = store.save_user_profile(profile)
    store.save_recommendation(signature, ranked_policy)
    history = store.get_previous_recommendations()

    assert signature
    assert len(history) == 1
    assert history[0]["recommendation"]["policy"]["policy_name"] == "Test Policy"


def test_critic_can_rerank_when_first_policy_has_clear_issues() -> None:
    critic = CriticAgent()
    profile = UserProfile(
        age=42,
        income=500000,
        dependents=2,
        assets=100000,
        liabilities=600000,
        insurance_goal="family_protection",
        net_worth=-500000,
        affordability_band="low",
        life_stage="family_builder",
        liability_ratio=1.2,
    )
    weak_policy = RankedPolicy(
        policy=Policy(
            policy_name="Weak Cover",
            policy_type="basic",
            coverage=1500000,
            premium=60000,
            target_profile=["health_security"],
            notes="Weak test policy",
        ),
        total_score=90.0,
        suitability_score=60.0,
        affordability_score=35.0,
        coverage_score=45.0,
        utility_score=82.0,
        premium_ratio=0.12,
        coverage_gap=3500000.0,
        tradeoff_summary="Coverage is weak and premium pressure is high.",
        explanation_points=["Weak fit."],
    )
    strong_policy = RankedPolicy(
        policy=Policy(
            policy_name="Strong Cover",
            policy_type="term_life",
            coverage=6000000,
            premium=25000,
            target_profile=["family_protection", "family_builder", "high", "has_dependents"],
            notes="Better test policy",
        ),
        total_score=88.0,
        suitability_score=95.0,
        affordability_score=90.0,
        coverage_score=90.0,
        utility_score=79.0,
        premium_ratio=0.05,
        coverage_gap=0.0,
        tradeoff_summary="Better balance of coverage and premium.",
        explanation_points=["Strong fit."],
    )

    result = critic.validate([weak_policy, strong_policy], profile, "high", 16000.0)

    assert result.validated_policy.policy.policy_name == "Strong Cover"
    assert result.confidence_score > 0
    assert result.issues


def test_policy_evaluation_uses_expected_loss_and_returns_top_three() -> None:
    profile = UserProfilingAgent().build_profile(
        UserInput(
            age=35,
            income=900000,
            dependents=2,
            assets=2000000,
            liabilities=1500000,
            insurance_goal="family_protection",
        )
    )
    ranked = PolicyEvaluationAgent().rank_policies(
        profile=profile,
        policies=load_policies(),
        risk_score=87.0,
        risk_label="high",
        expected_loss=16000.0,
    )

    assert len(ranked[:3]) == 3
    assert all(policy.utility_score >= 0 for policy in ranked[:3])
    assert "expected loss of 16000" in ranked[0].tradeoff_summary.lower()


def test_recommendation_response_includes_agentic_fields() -> None:
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
    assert result.final_recommendation.policy.policy_name == result.best_policy.policy.policy_name
    assert len(result.top_policies) == 3
    assert result.risk_score > 0
    assert result.expected_loss > 0  # Now dynamic, not hardcoded 16000
    assert result.confidence_score > 0
    assert result.critic_issues
    assert result.memory_snapshot.profile_signature
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
    assert result.best_policy.policy.policy_name
    assert result.final_recommendation.policy.policy_name == result.best_policy.policy.policy_name


def test_different_profiles_produce_different_expected_losses() -> None:
    """End-to-end: two different users should get different expected losses."""
    agent = RecommendationAgent()

    young_result = agent.recommend(
        UserInput(age=22, income=300000, dependents=0, assets=0, liabilities=0, insurance_goal="health_security")
    )
    senior_result = agent.recommend(
        UserInput(age=55, income=1500000, dependents=3, assets=5000000, liabilities=2000000, insurance_goal="family_protection")
    )

    assert young_result.expected_loss != senior_result.expected_loss
