"""Risk Analysis Agent."""

from __future__ import annotations

from typing import Literal, Tuple

from app.models import UserProfile

class RiskAnalysisAgent:
    """Compute a transparent insurance need / risk score."""

    def calculate_risk(self, profile: UserProfile) -> Tuple[float, Literal["low", "moderate", "high"]]:
        """
        Compute a risk score directly on a 0-100 scale.
        All factor max contributions sum to exactly 100.
        """

        # ── Insurance Need / Financial Risk Factors ──
        # Older customers usually carry higher underwriting/claim risk, while
        # dependents increase the financial protection need.
        age_score = (
            6
            if profile.age < 30
            else 10
            if profile.age < 40
            else 14
            if profile.age < 50
            else 18
            if profile.age < 60
            else 20
        )
        dependent_score = (
            0
            if profile.dependents == 0
            else 8
            if profile.dependents == 1
            else 14
            if profile.dependents == 2
            else 18
            if profile.dependents == 3
            else 20
        )
        liability_score = round(min(profile.liability_ratio * 15, 15), 2)
        income_score = 12 if profile.income < 500000 else 8 if profile.income < 1200000 else 4
        net_worth_score = 8 if profile.net_worth <= 0 else 5 if profile.net_worth < 1000000 else 2

        # ── Health Risk Factor ──
        # health_risk_score is pre-computed by UserProfilingAgent on a 0-25 scale
        health_score = profile.health_risk_score

        risk_score = round(
            age_score
            + dependent_score
            + liability_score
            + income_score
            + net_worth_score
            + health_score,
            2,
        )

        # Labels
        if risk_score < 40:
            risk_label: Literal["low", "moderate", "high"] = "low"
        elif risk_score < 70:
            risk_label = "moderate"
        else:
            risk_label = "high"

        return risk_score, risk_label
