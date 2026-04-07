"""Policy Evaluation Agent."""

from __future__ import annotations

from typing import List

from app.models import Policy, RankedPolicy, UserProfile


class PolicyEvaluationAgent:
    """Rank policies with a simple utility-style scoring rule."""

    def rank_policies(
        self,
        profile: UserProfile,
        policies: List[Policy],
        risk_score: float,
        risk_label: str,
    ) -> List[RankedPolicy]:
        """Score and rank policies from best to worst."""
        ranked: List[RankedPolicy] = []

        recommended_coverage = max(profile.income * 10, 500000)
        annual_budget = max(profile.income * 0.06, 10000)

        for policy in policies:
            suitability_score, suitability_reasons = self._score_suitability(profile, policy, risk_label)
            affordability_score = self._score_affordability(policy.premium, annual_budget)
            coverage_score = self._score_coverage(policy.coverage, recommended_coverage, risk_score)

            total_score = round(
                (suitability_score * 0.45) + (coverage_score * 0.35) + (affordability_score * 0.20),
                2,
            )

            explanation_points = suitability_reasons + [
                f"Coverage {self._coverage_phrase(policy.coverage, recommended_coverage)} the estimated need.",
                f"Premium is {self._premium_phrase(policy.premium, annual_budget)} for the user's budget.",
            ]

            ranked.append(
                RankedPolicy(
                    policy=policy,
                    total_score=total_score,
                    suitability_score=round(suitability_score, 2),
                    affordability_score=round(affordability_score, 2),
                    coverage_score=round(coverage_score, 2),
                    explanation_points=explanation_points,
                )
            )

        return sorted(ranked, key=lambda item: item.total_score, reverse=True)

    def _score_suitability(self, profile: UserProfile, policy: Policy, risk_label: str) -> tuple[float, List[str]]:
        score = 40.0
        reasons: List[str] = []

        if profile.insurance_goal in policy.target_profile:
            score += 25
            reasons.append(f"It directly aligns with the goal '{profile.insurance_goal}'.")

        if profile.life_stage in policy.target_profile:
            score += 15
            reasons.append(f"It suits the user's life stage '{profile.life_stage}'.")

        if risk_label in policy.target_profile:
            score += 20
            reasons.append(f"It matches a {risk_label} risk profile.")

        if profile.dependents > 0 and "has_dependents" in policy.target_profile:
            score += 10
            reasons.append("It is designed for users with dependents.")

        return min(score, 100.0), reasons or ["It provides a general fit across the user's needs."]

    def _score_affordability(self, premium: float, annual_budget: float) -> float:
        if premium <= annual_budget * 0.6:
            return 95.0
        if premium <= annual_budget:
            return 80.0
        if premium <= annual_budget * 1.25:
            return 60.0
        return 35.0

    def _score_coverage(self, coverage: float, recommended_coverage: float, risk_score: float) -> float:
        target = recommended_coverage if risk_score >= 40 else recommended_coverage * 0.75
        ratio = coverage / target
        if 0.9 <= ratio <= 1.2:
            return 95.0
        if 0.7 <= ratio < 0.9 or 1.2 < ratio <= 1.5:
            return 80.0
        if 0.5 <= ratio < 0.7:
            return 60.0
        return 45.0

    def _coverage_phrase(self, coverage: float, recommended_coverage: float) -> str:
        if coverage >= recommended_coverage:
            return "meets or exceeds"
        if coverage >= recommended_coverage * 0.75:
            return "is close to"
        return "is below"

    def _premium_phrase(self, premium: float, annual_budget: float) -> str:
        if premium <= annual_budget:
            return "comfortable"
        if premium <= annual_budget * 1.25:
            return "slightly stretched"
        return "expensive"
