"""Risk Analysis Agent."""

from __future__ import annotations

from typing import Literal, Tuple

from app.models import UserProfile


class RiskAnalysisAgent:
    """Compute a transparent insurance need / risk score."""

    def calculate_risk(self, profile: UserProfile) -> Tuple[float, Literal["low", "moderate", "high"]]:
        """
        Compute a score on a 0-100 scale.

        Formula:
        - Age contribution: middle-aged users get slightly higher need
        - Dependents increase protection need
        - Higher liabilities increase risk
        - Lower income increases affordability pressure
        - Low net worth increases vulnerability
        """
        age_score = 15 if profile.age < 30 else 20 if profile.age < 50 else 12
        dependent_score = min(profile.dependents * 10, 30)
        liability_score = min(profile.liability_ratio * 25, 25)
        income_score = 20 if profile.income < 500000 else 12 if profile.income < 1200000 else 6
        net_worth_score = 15 if profile.net_worth <= 0 else 10 if profile.net_worth < 1000000 else 5

        risk_score = round(age_score + dependent_score + liability_score + income_score + net_worth_score, 2)

        if risk_score < 40:
            risk_label: Literal["low", "moderate", "high"] = "low"
        elif risk_score < 70:
            risk_label = "moderate"
        else:
            risk_label = "high"

        return risk_score, risk_label
