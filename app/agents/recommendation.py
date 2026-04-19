"""Recommendation flow runner."""

from __future__ import annotations

import os
import time
from typing import List

from app.models import (
    RecommendationResponse,
    UserInput,
)
from app.core.orchestrator import OrchestratorAgent
from app.agents.goal_planner import GoalPlannerAgent
from app.utils.regulatory import IRDAI_REGULATORY_NOTE

class RecommendationAgent:
    """Main recommendation entry point."""

    def __init__(self) -> None:
        self.orchestrator = OrchestratorAgent()

    def recommend(self, user_input: UserInput) -> RecommendationResponse:
        """Run agent orchestrator."""
        final_state = self.orchestrator.run_loop(user_input)
        
        best_policy = final_state.get("best_policy")
        critic_result = final_state.get("critic_result")
        compliance_report = final_state.get("compliance_report")
        
        # Build text explanation
        planner = GoalPlannerAgent()
        explanation = planner.build_explanation(
            best_policy=best_policy,
            risk_label=final_state.get("risk_label"),
            expected_loss=final_state.get("expected_loss"),
            critic_issues=critic_result.issues if critic_result else [],
            compliance_issues=compliance_report["issues"] if compliance_report else []
        )

        return RecommendationResponse(
            user_profile=final_state.get("user_profile"),
            risk_score=final_state.get("risk_score"),
            risk_label=final_state.get("risk_label"),
            expected_loss=final_state.get("expected_loss"),
            scenario_breakdown=final_state.get("scenario_result").scenario_breakdown,
            best_policy=best_policy,
            final_recommendation=best_policy,
            top_policies=final_state.get("top_policies"),
            critic_issues=critic_result.issues if critic_result else [],
            confidence_score=critic_result.confidence_score if critic_result else 0.0,
            memory_snapshot=final_state.get("memory_snapshot"),
            explanation=explanation,
            regulatory_note=IRDAI_REGULATORY_NOTE,
            compliance_report=compliance_report,
            agent_trace=final_state.get("trace")
        )
