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

        # ── Financial Risk Factors ──
        age_score = 10 if profile.age < 30 else 15 if profile.age < 50 else 8
        dependent_score = min(profile.dependents * 7, 20)
        liability_score = round(min(profile.liability_ratio * 15, 15), 2)
        income_score = 15 if profile.income < 500000 else 9 if profile.income < 1200000 else 4
        net_worth_score = 10 if profile.net_worth <= 0 else 7 if profile.net_worth < 1000000 else 3

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