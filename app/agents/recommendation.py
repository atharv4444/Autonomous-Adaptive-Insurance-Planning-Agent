"""Recommendation Agent — orchestrates the full multi-agent pipeline with tracing."""

from __future__ import annotations

import os
import time
from typing import List

from app.models import (
    RecommendationResponse,
    UserInput,
)
from app.agents.goal_planner import GoalPlannerAgent

class RecommendationAgent:
    """Coordinate the end-to-end recommendation flow by delegating to the GoalPlannerAgent."""

    def __init__(self) -> None:
        self.planner = GoalPlannerAgent()

    def recommend(self, user_input: UserInput) -> RecommendationResponse:
        """Execute the goal-based plan via the Planner Agent."""
        return self.planner.execute_plan(user_input)
