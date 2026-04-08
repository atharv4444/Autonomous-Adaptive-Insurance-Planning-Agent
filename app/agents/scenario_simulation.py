"""Scenario Simulation Agent — Profile-aware risk scenario estimation."""

from __future__ import annotations

from app.models import ScenarioBreakdown, ScenarioSimulationResult, UserProfile


class ScenarioSimulationAgent:
    """Simulate real-world loss scenarios dynamically based on the user's profile."""

    def simulate(self, profile: UserProfile | None = None) -> ScenarioSimulationResult:
        """
        Return scenario impacts and total expected loss.

        When a UserProfile is provided the probabilities and costs are adjusted
        according to age, income, dependents, liabilities, and insurance goal.
        Falls back to sensible baseline values when no profile is given.
        """
        if profile is None:
            return self._static_simulation()

        breakdown: list[ScenarioBreakdown] = []

        # ── Medical Emergency ──
        med_prob = self._medical_probability(profile)
        med_cost = self._medical_cost(profile)
        breakdown.append(
            ScenarioBreakdown(
                scenario_name="medical_emergency",
                probability=round(med_prob, 4),
                cost=round(med_cost, 2),
                expected_impact=round(med_prob * med_cost, 2),
            )
        )

        # ── Accident ──
        acc_prob = self._accident_probability(profile)
        acc_cost = self._accident_cost(profile)
        breakdown.append(
            ScenarioBreakdown(
                scenario_name="accident",
                probability=round(acc_prob, 4),
                cost=round(acc_cost, 2),
                expected_impact=round(acc_prob * acc_cost, 2),
            )
        )

        # ── Income Loss ──
        inc_prob = self._income_loss_probability(profile)
        inc_cost = self._income_loss_cost(profile)
        breakdown.append(
            ScenarioBreakdown(
                scenario_name="income_loss",
                probability=round(inc_prob, 4),
                cost=round(inc_cost, 2),
                expected_impact=round(inc_prob * inc_cost, 2),
            )
        )

        expected_loss = round(sum(item.expected_impact for item in breakdown), 2)
        return ScenarioSimulationResult(expected_loss=expected_loss, scenario_breakdown=breakdown)

    # ── Private helpers for dynamic calculations ──

    def _medical_probability(self, profile: UserProfile) -> float:
        """Higher for older users and those focused on health."""
        base = 0.15
        if profile.age > 50:
            base += 0.20
        elif profile.age > 40:
            base += 0.10
        elif profile.age < 25:
            base -= 0.05
        if profile.insurance_goal == "health_security":
            base += 0.05
        if profile.dependents > 2:
            base += 0.05
        return min(max(base, 0.05), 0.60)

    def _medical_cost(self, profile: UserProfile) -> float:
        """Scale medical costs relative to income and age bracket."""
        base_cost = max(profile.income * 0.05, 25000.0)
        if profile.age > 50:
            base_cost *= 1.8
        elif profile.age > 40:
            base_cost *= 1.3
        return round(base_cost, 2)

    def _accident_probability(self, profile: UserProfile) -> float:
        """Younger users have slightly higher accident probability."""
        base = 0.10
        if profile.age < 30:
            base += 0.05
        elif profile.age > 50:
            base -= 0.03
        return min(max(base, 0.03), 0.40)

    def _accident_cost(self, profile: UserProfile) -> float:
        """Accident costs scale with income and dependents."""
        base_cost = max(profile.income * 0.08, 40000.0)
        if profile.dependents > 0:
            base_cost *= 1.0 + (profile.dependents * 0.1)
        return round(base_cost, 2)

    def _income_loss_probability(self, profile: UserProfile) -> float:
        """Higher when liabilities are significant relative to income."""
        base = 0.05
        if profile.liability_ratio > 1.0:
            base += 0.15
        elif profile.liability_ratio > 0.5:
            base += 0.08
        if profile.net_worth < 0:
            base += 0.05
        return min(max(base, 0.02), 0.40)

    def _income_loss_cost(self, profile: UserProfile) -> float:
        """Income loss cost is a multiple of annual income."""
        multiplier = 1.5
        if profile.dependents > 2:
            multiplier = 2.5
        elif profile.dependents > 0:
            multiplier = 2.0
        if profile.liability_ratio > 0.5:
            multiplier += 0.5
        return round(profile.income * multiplier, 2)

    # ── Fallback for backward compatibility ──

    def _static_simulation(self) -> ScenarioSimulationResult:
        """Legacy static scenarios used when no profile is available."""
        static_scenarios = (
            ("medical_emergency", 0.2, 30000.0),
            ("accident", 0.1, 50000.0),
            ("income_loss", 0.05, 100000.0),
        )
        breakdown: list[ScenarioBreakdown] = []
        for name, prob, cost in static_scenarios:
            breakdown.append(
                ScenarioBreakdown(
                    scenario_name=name,
                    probability=prob,
                    cost=cost,
                    expected_impact=round(prob * cost, 2),
                )
            )
        expected_loss = round(sum(item.expected_impact for item in breakdown), 2)
        return ScenarioSimulationResult(expected_loss=expected_loss, scenario_breakdown=breakdown)
