"""Critic Agent — enhanced with optional Gemini LLM critique."""

from __future__ import annotations

import json
import logging
from typing import List

from app.models import CriticResult, RankedPolicy, UserProfile
import app.llm.client as llm
from app.llm.prompts import critic_prompt

logger = logging.getLogger(__name__)


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

        # --- LLM critique (preferred) ---
        if llm.is_available():
            result = self._llm_validate(candidates, profile, risk_label, expected_loss)
            if result is not None:
                return result

        # --- Rule-based fallback ---
        return self._rule_based_validate(candidates, profile, risk_label, expected_loss)

    # -----------------------------------------------------------------------
    # LLM critic
    # -----------------------------------------------------------------------
    def _llm_validate(
        self,
        candidates: List[RankedPolicy],
        profile: UserProfile,
        risk_label: str,
        expected_loss: float,
    ) -> CriticResult | None:
        profile_data = {
            "age": profile.age,
            "income": profile.income,
            "dependents": profile.dependents,
            "life_stage": profile.life_stage,
            "affordability_band": profile.affordability_band,
            "insurance_goal": profile.insurance_goal,
            "net_worth": profile.net_worth,
            "liability_ratio": profile.liability_ratio,
        }
        policies_data = [
            {
                "policy_name": c.policy.policy_name,
                "coverage": c.policy.coverage,
                "premium": c.policy.premium,
                "total_score": c.total_score,
                "premium_ratio": c.premium_ratio,
                "coverage_gap": c.coverage_gap,
                "tradeoff_summary": c.tradeoff_summary,
            }
            for c in candidates
        ]

        prompt = critic_prompt(
            json.dumps(profile_data, indent=2),
            json.dumps(policies_data, indent=2),
            risk_label,
            expected_loss,
        )
        result = llm.chat_json(prompt)

        if not result or "recommended_policy_name" not in result:
            logger.warning("LLM critic returned no usable data; falling back to rules.")
            return None

        recommended_name = result["recommended_policy_name"]
        # Find the matching policy (default to top-ranked if LLM name doesn't match exactly)
        best_candidate = next(
            (c for c in candidates if c.policy.policy_name == recommended_name),
            candidates[0],
        )

        issues: List[str] = result.get("issues", [])
        critique_summary = result.get("critique_summary", "")
        if critique_summary:
            issues.append(f"AI Critique: {critique_summary}")

        confidence_score = float(result.get("confidence_score", 75))

        return CriticResult(
            validated_policy=best_candidate,
            issues=issues or ["No major issues detected by the AI critic."],
            confidence_score=confidence_score,
        )

    # -----------------------------------------------------------------------
    # Rule-based fallback (original logic preserved)
    # -----------------------------------------------------------------------
    def _rule_based_validate(
        self,
        candidates: List[RankedPolicy],
        profile: UserProfile,
        risk_label: str,
        expected_loss: float,
    ) -> CriticResult:
        best_candidate = candidates[0]
        best_evaluation = self._evaluate_candidate(best_candidate, profile, risk_label, expected_loss)

        for candidate in candidates[1:]:
            evaluation = self._evaluate_candidate(candidate, profile, risk_label, expected_loss)
            utility_gap = best_candidate.utility_score - candidate.utility_score
            if evaluation["critical_issues"] < best_evaluation["critical_issues"] and utility_gap <= 10:
                best_candidate = candidate
                best_evaluation = evaluation

        return CriticResult(
            validated_policy=best_candidate,
            issues=best_evaluation["issues"],
            confidence_score=round(max(0.0, min(100.0, 100 - best_evaluation["penalty"])), 2),
        )

    def _evaluate_candidate(
        self,
        candidate: RankedPolicy,
        profile: UserProfile,
        risk_label: str,
        expected_loss: float,
    ) -> dict:
        recommended_coverage = max(profile.income * 10, 500000.0)
        if risk_label == "high":
            recommended_coverage += expected_loss

        issues: List[str] = []
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

        if (
            profile.insurance_goal not in candidate.policy.target_profile
            or risk_label not in candidate.policy.target_profile
        ):
            issues.append("mismatch_with_risk_level: policy fit is weaker for the user's goal or risk level.")
            penalty += 15

        if not issues:
            issues.append("No major issues detected by the critic. The recommendation is consistent with the user profile.")
            penalty += 5

        return {"issues": issues, "penalty": penalty, "critical_issues": critical_issues}
