"""Planner logic."""

from __future__ import annotations

import os
import time
from typing import List, Optional

from app.core.plan import Plan
from app.models import RankedPolicy
from app.llm.gemini_explainer import generate_explanation_with_gemini, gemini_key_present

class GoalPlannerAgent:
    """
    Generates execution plan.
    """

    def __init__(self) -> None:
        self.primary_goal = "Find the most suitable policy available for the customer"

    def generate_plan(self) -> Plan:
        """Returns default steps."""
        steps = [
            "ProfileUserTool",
            "CalculateRiskTool",
            "SimulateScenarioTool",
            "EvaluatePoliciesTool",
            "ValidateCriticTool",
            "LearnAdaptiveTool",
            "CheckComplianceTool",
            "PersistMemoryTool"
        ]
        return Plan(steps)

    def revise_plan_on_rejection(self) -> list[str]:
        """Returns steps for failure recovery."""
        revised_steps = [
            "EvaluatePoliciesTool",
            "ValidateCriticTool",
            "LearnAdaptiveTool",
            "PersistMemoryTool"
        ]
        return revised_steps

    def build_explanation(
        self,
        best_policy: RankedPolicy,
        risk_label: str,
        expected_loss: float,
        critic_issues: list[str],
        compliance_issues: list[str] = None,
    ) -> str:
        """Build final text description."""
        critic_summary = critic_issues[0] if critic_issues else "The critic found no major issues."
        compliance_summary = ". ".join(compliance_issues) if compliance_issues else "No regulatory compliance issues flagged."

        template = (
            f"{best_policy.policy.policy_name} is recommended because it balances high coverage with an acceptable premium "
            f"for a {risk_label} risk profile. "
            f"Its premium-to-income ratio is {best_policy.premium_ratio:.2%} and the tradeoff remains favorable because {best_policy.tradeoff_summary} "
            f"Critic review: {critic_summary}. Compliance check: {compliance_summary}."
        )

        if not gemini_key_present():
            return template

        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        prompt = (
            "You are an insurance planning assistant. Write a concise, user-friendly explanation (2-5 sentences) "
            "for why the recommended policy was chosen. Avoid disclaimers. Don't mention internal agent names. "
            "Use INR currency symbol ₹ where relevant.\n\n"
            f"Recommended policy: {best_policy.policy.policy_name}\n"
            f"Policy type: {best_policy.policy.policy_type}\n"
            f"Risk label: {risk_label}\n"
            f"Tradeoff summary: {best_policy.tradeoff_summary}\n"
            f"Critic note: {critic_summary}\n"
            f"Regulatory compliance note: {compliance_summary}\n"
        )

        llm_text = generate_explanation_with_gemini(prompt=prompt, model=model)
        return llm_text or template
