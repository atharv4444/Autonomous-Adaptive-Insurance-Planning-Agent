"""Scenario Simulation Agent."""

from __future__ import annotations

from app.models import ScenarioBreakdown, ScenarioSimulationResult


class ScenarioSimulationAgent:
    """Simulate simple real-world loss scenarios for decision support."""

    SCENARIOS = (
        ("medical_emergency", 0.2, 30000.0),
        ("accident", 0.1, 50000.0),
        ("income_loss", 0.05, 100000.0),
    )

    def simulate(self) -> ScenarioSimulationResult:
        """Return fixed scenario impacts and total expected loss."""
        breakdown: list[ScenarioBreakdown] = []

        for scenario_name, probability, cost in self.SCENARIOS:
            breakdown.append(
                ScenarioBreakdown(
                    scenario_name=scenario_name,
                    probability=probability,
                    cost=cost,
                    expected_impact=round(probability * cost, 2),
                )
            )

        expected_loss = round(sum(item.expected_impact for item in breakdown), 2)

        # TODO: Replace static scenario assumptions with personalized risk estimation.
        # TODO: Integrate external data or APIs for real-world risk feeds.
        # TODO: Calibrate scenario probabilities with ML-based forecasting models.
        return ScenarioSimulationResult(expected_loss=expected_loss, scenario_breakdown=breakdown)
