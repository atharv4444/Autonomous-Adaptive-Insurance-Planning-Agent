"""Policy Evaluation Agent — enhanced with optional Gemini LLM scoring."""

from __future__ import annotations

import json
import logging
from typing import List

from app.models import Policy, RankedPolicy, UserProfile
from app.agents.rl_policy_agent import RLPolicyAgent
import app.llm.client as llm
from app.llm.prompts import policy_ranking_prompt

logger = logging.getLogger(__name__)


class PolicyEvaluationAgent:
    """Rank policies with utility scoring blended with optional LLM suitability scores."""

    def __init__(self):
        self.rl_agent = RLPolicyAgent()

    def rank_policies(
        self,
        profile: UserProfile,
        policies: List[Policy],
        risk_score: float,
        risk_label: str,
        expected_loss: float,
    ) -> List[RankedPolicy]:
        """Score and rank policies from best to worst."""
        ranked_inputs: List[dict] = []

        recommended_coverage = max(profile.income * 10, 500000)
        if risk_label == "high":
            recommended_coverage += expected_loss
        annual_budget = max(profile.income * 0.06, 10000)
        premium_weight = self._premium_weight(profile.affordability_band)

        # RL State Vectorization
        state = [
            profile.age / 70.0,
            profile.income / 3_000_000.0,
            profile.dependents / 5.0,
            profile.net_worth / 10_000_000.0,
            risk_score / 100.0,
        ]
        ai_scores = self.rl_agent.get_policy_rankings(state, policies)

        # --- LLM suitability scoring (optional, falls back to rule-based) ---
        llm_scores: dict[str, dict] = {}
        if llm.is_available():
            llm_scores = self._llm_score_policies(profile, policies, risk_label)

        for i, policy in enumerate(policies):
            # Use LLM suitability if available, otherwise rule-based
            if policy.policy_name in llm_scores:
                llm_entry = llm_scores[policy.policy_name]
                suitability_score = float(llm_entry.get("llm_suitability_score", 50))
                suitability_reasons = [llm_entry.get("llm_reasoning", "LLM-evaluated suitability.")]
            else:
                suitability_score, suitability_reasons = self._score_suitability(profile, policy, risk_label)

            affordability_score = self._score_affordability(policy.premium, annual_budget)
            coverage_score = self._score_coverage(policy.coverage, recommended_coverage, risk_score)
            raw_utility = policy.coverage - (policy.premium * premium_weight) - expected_loss
            premium_ratio = round(policy.premium / profile.income, 4) if profile.income > 0 else 1.0
            coverage_gap = round(max(recommended_coverage - policy.coverage, 0.0), 2)

            explanation_points = suitability_reasons + [
                f"Coverage {self._coverage_phrase(policy.coverage, recommended_coverage)} the estimated need.",
                f"Premium is {self._premium_phrase(policy.premium, annual_budget)} for the user's budget.",
                f"Expected loss of {expected_loss:.0f} was included in the utility calculation.",
            ]

            ranked_inputs.append({
                "policy": policy,
                "raw_utility": raw_utility,
                "suitability_score": round(suitability_score, 2),
                "affordability_score": round(affordability_score, 2),
                "coverage_score": round(coverage_score, 2),
                "premium_ratio": premium_ratio,
                "coverage_gap": coverage_gap,
                "tradeoff_summary": self._build_tradeoff_summary(
                    policy.coverage, recommended_coverage,
                    policy.premium, annual_budget, expected_loss,
                ),
                "explanation_points": explanation_points,
                "ai_score": ai_scores[i] if i < len(ai_scores) else 0.0,
            })

        utility_scores = self._normalize_utilities([item["raw_utility"] for item in ranked_inputs])
        ranked: List[RankedPolicy] = []

        for index, item in enumerate(ranked_inputs):
            utility_score = utility_scores[index]
            total_score = round(
                (utility_score * 0.40)
                + (float(item["suitability_score"]) * 0.25)
                + (float(item["coverage_score"]) * 0.20)
                + (float(item["affordability_score"]) * 0.15),
                2,
            )
            ranked.append(RankedPolicy(
                policy=item["policy"],
                total_score=total_score,
                suitability_score=float(item["suitability_score"]),
                affordability_score=float(item["affordability_score"]),
                coverage_score=float(item["coverage_score"]),
                utility_score=utility_score,
                ai_score=float(item["ai_score"]),
                premium_ratio=float(item["premium_ratio"]),
                coverage_gap=float(item["coverage_gap"]),
                tradeoff_summary=str(item["tradeoff_summary"]),
                explanation_points=list(item["explanation_points"]),
            ))

        return sorted(ranked, key=lambda item: (item.total_score, item.utility_score), reverse=True)

    # -----------------------------------------------------------------------
    # LLM scoring
    # -----------------------------------------------------------------------
    def _llm_score_policies(
        self,
        profile: UserProfile,
        policies: List[Policy],
        risk_label: str,
    ) -> dict[str, dict]:
        """Ask Gemini to score each policy's suitability. Returns {policy_name: {...}}."""
        profile_data = {
            "age": profile.age,
            "income": profile.income,
            "dependents": profile.dependents,
            "life_stage": profile.life_stage,
            "affordability_band": profile.affordability_band,
            "insurance_goal": profile.insurance_goal,
            "net_worth": profile.net_worth,
            "risk_label": risk_label,
        }
        policies_data = [
            {
                "policy_name": p.policy_name,
                "coverage": p.coverage,
                "premium": p.premium,
                "target_profile": p.target_profile,
            }
            for p in policies
        ]

        prompt = policy_ranking_prompt(
            json.dumps(profile_data, indent=2),
            json.dumps(policies_data, indent=2),
        )

        result = llm.chat_json(prompt)
        if not result or "rankings" not in result:
            logger.warning("LLM policy ranking returned no usable data; using rule-based fallback.")
            return {}

        return {
            entry["policy_name"]: entry
            for entry in result["rankings"]
            if "policy_name" in entry
        }

    # -----------------------------------------------------------------------
    # Rule-based helpers (fallback + utility components)
    # -----------------------------------------------------------------------
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

    def _premium_weight(self, affordability_band: str) -> float:
        if affordability_band == "low":
            return 1.5
        if affordability_band == "high":
            return 0.7
        return 1.0

    def _normalize_utilities(self, raw_utilities: List[object]) -> List[float]:
        values = [float(v) for v in raw_utilities]
        minimum, maximum = min(values), max(values)
        if maximum == minimum:
            return [75.0 for _ in values]
        return [round(((v - minimum) / (maximum - minimum)) * 100, 2) for v in values]

    def _build_tradeoff_summary(
        self,
        coverage: float,
        recommended_coverage: float,
        premium: float,
        annual_budget: float,
        expected_loss: float,
    ) -> str:
        return (
            f"This policy {self._coverage_phrase(coverage, recommended_coverage)} the target coverage, "
            f"keeps premium {self._premium_phrase(premium, annual_budget)}, "
            f"and was evaluated against an expected loss of {expected_loss:.0f}."
        )
