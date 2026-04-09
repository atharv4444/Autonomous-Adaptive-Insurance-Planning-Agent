"""User Profiling Agent."""

from __future__ import annotations

from app.models import UserInput, UserProfile


class UserProfilingAgent:
    """Convert raw user input into a normalized user profile."""

    def build_profile(self, user_input: UserInput) -> UserProfile:
        """Derive simple, explainable profile attributes from inputs."""
        net_worth = user_input.assets - user_input.liabilities
        if user_input.income > 0:
            liability_ratio = user_input.liabilities / user_input.income
        elif user_input.liabilities == 0:
            # No income AND no liabilities → neutral, no debt pressure
            liability_ratio = 0.0
        else:
            # No income but has liabilities → very high risk, cap at 2.0
            liability_ratio = 2.0

        if user_input.income < 500000:
            affordability_band = "low"
        elif user_input.income < 1200000:
            affordability_band = "medium"
        else:
            affordability_band = "high"

        if user_input.age < 30:
            life_stage = "early_career"
        elif user_input.age < 50:
            life_stage = "family_builder"
        else:
            life_stage = "pre_retirement"

        # ── Health Risk Score (0-30 scale) ──
        health_risk_score = self._compute_health_risk(user_input)

        return UserProfile(
            age=user_input.age,
            income=user_input.income,
            dependents=user_input.dependents,
            assets=user_input.assets,
            liabilities=user_input.liabilities,
            insurance_goal=user_input.insurance_goal,
            net_worth=net_worth,
            affordability_band=affordability_band,
            life_stage=life_stage,
            liability_ratio=round(liability_ratio, 2),
            is_smoker=user_input.is_smoker,
            alcohol_consumption=user_input.alcohol_consumption,
            has_severe_health_issues=user_input.has_severe_health_issues,
            health_risk_score=round(health_risk_score, 2),
        )

    @staticmethod
    def _compute_health_risk(user_input: UserInput) -> float:
        """
        Compute a health risk sub-score on a 0-25 scale.

        Smoking:           0 or 10 pts
        Alcohol:           0 / 2 / 5 / 8 pts
        Severe Conditions: 0 or 7 pts
        """
        score = 0.0

        # Smoking — strongest single lifestyle risk factor
        if user_input.is_smoker:
            score += 10

        # Alcohol consumption — graduated scale
        alcohol_scores = {"none": 0, "occasional": 2, "moderate": 5, "heavy": 8}
        score += alcohol_scores.get(user_input.alcohol_consumption, 0)

        # Pre-existing severe health issues
        if user_input.has_severe_health_issues:
            score += 7

        return score

