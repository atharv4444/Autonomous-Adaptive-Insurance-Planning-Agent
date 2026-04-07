"""User Profiling Agent."""

from __future__ import annotations

from app.models import UserInput, UserProfile


class UserProfilingAgent:
    """Convert raw user input into a normalized user profile."""

    def build_profile(self, user_input: UserInput) -> UserProfile:
        """Derive simple, explainable profile attributes from inputs."""
        net_worth = user_input.assets - user_input.liabilities
        liability_ratio = (
            user_input.liabilities / user_input.income if user_input.income > 0 else 1.0
        )

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
        )
