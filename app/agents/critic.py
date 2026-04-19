"""Critic Agent."""

from __future__ import annotations

from typing import List

from app.models import CriticResult, RankedPolicy, UserProfile


class CriticAgent:
    """Validate top recommendations and rerank when a better candidate is obvious."""

    def validate(
        self,
        ranked_policies: List[RankedPolicy],
        profile: UserProfile,
        risk_label: str,
        expected_loss: float,
    ) -> CriticResult:
        """Inspect the top-ranked candidates and return a validated choice."""
        candidates = ranked_policies[:3]
        best_candidate = candidates[0]
        best_evaluation = self._evaluate_candidate(best_candidate, profile, risk_label, expected_loss)

        for candidate in candidates[1:]:
            evaluation = self._evaluate_candidate(candidate, profile, risk_label, expected_loss)
            utility_gap = best_candidate.utility_score - candidate.utility_score

            if evaluation["critical_issues"] < best_evaluation["critical_issues"] and utility_gap <= 10:
                best_candidate = candidate
                best_evaluation = evaluation

        confidence = round(max(0.0, min(100.0, 100 - best_evaluation["penalty"])), 2)
        
        # Rejection Mechanism: If the best policy still has too many critical issues, trigger replanning
        requires_replanning = False
        if confidence < 50.0 or best_evaluation["critical_issues"] >= 2:
            requires_replanning = True
            best_evaluation["issues"].append("[CRITICAL REJECTION]: Output is suboptimal. Triggering re-planning.")

        return CriticResult(
            validated_policy=best_candidate,
            issues=best_evaluation["issues"],
            confidence_score=confidence,
            requires_replanning=requires_replanning
        )

    def _evaluate_candidate(
        self,
        candidate: RankedPolicy,
        profile: UserProfile,
        risk_label: str,
        expected_loss: float,
    ) -> dict[str, object]:
        recommended_coverage = max(profile.income * 10, 500000.0)
        if risk_label == "high":
            recommended_coverage += expected_loss

        issues: list[str] = []
        penalty = 0.0
        critical_issues = 0

        if candidate.policy.coverage < recommended_coverage * 0.75:
            issues.append("underinsured: coverage is materially below the user's estimated need.")
            penalty += 30
            critical_issues += 1

        if candidate.premium_ratio > 0.08:
            issues.append("overpriced_policy: premium is high relative to annual income.")
            penalty += 20
            critical_issues += 1

        if profile.insurance_goal not in candidate.policy.target_profile or risk_label not in candidate.policy.target_profile:
            issues.append("mismatch_with_risk_level: policy fit is weaker for the user's goal or risk level.")
            penalty += 15

        if not issues:
            issues.append("No major issues detected by the critic. The recommendation is consistent with the user profile.")
            penalty += 5

        # TODO: Add LLM-assisted critique to explain borderline policy tradeoffs.
        # TODO: Add regulatory and compliance checks before final policy approval.
        return {
            "issues": issues,
            "penalty": penalty,
            "critical_issues": critical_issues,
        }
