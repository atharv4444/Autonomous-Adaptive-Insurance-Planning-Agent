"""Scenario Simulation Agent — Data-driven risk scenario estimation.

This agent uses **trained Logistic Regression** models to predict the
probability of each scenario and **trained Linear Regression** models
to predict the expected cost.  All weights were learned from a 3,000-
sample synthetic actuarial dataset via gradient descent (probability)
and OLS closed-form solution (cost).

Model weights are loaded from  app/models/scenario_models.json
"""

from __future__ import annotations

import json
import os
from typing import Optional

import numpy as np

from app.models import ScenarioBreakdown, ScenarioSimulationResult, UserProfile


class ScenarioSimulationAgent:
    """Simulate real-world loss scenarios using **trained ML models**."""

    def __init__(self) -> None:
        self._models_loaded = False
        self._load_models()

    # ── Model loading ────────────────────────────────────────────────

    def _load_models(self) -> None:
        """Attempt to load trained weights from disk."""
        model_path = os.path.join("app", "models", "scenario_models.json")
        if not os.path.exists(model_path):
            return

        with open(model_path, "r") as f:
            data = json.load(f)

        self._w_med_prob = np.array(data["med_prob_weights"])
        self._w_acc_prob = np.array(data["acc_prob_weights"])
        self._w_inc_prob = np.array(data["inc_prob_weights"])

        self._w_med_cost = np.array(data["med_cost_weights"])
        self._w_acc_cost = np.array(data["acc_cost_weights"])
        self._w_inc_cost = np.array(data["inc_cost_weights"])

        self._cost_scale = float(data.get("cost_scale", 1_000_000.0))
        self._models_loaded = True

    # ── Inference helpers ────────────────────────────────────────────

    @staticmethod
    def _sigmoid(x: float) -> float:
        return float(1.0 / (1.0 + np.exp(-np.clip(x, -30, 30))))

    def _predict_prob(self, features: np.ndarray, w: np.ndarray) -> float:
        """Logistic regression: sigmoid(bias + X @ w[1:])."""
        xb = np.concatenate([[1.0], features])
        return float(np.clip(self._sigmoid(xb @ w), 0.03, 0.60))

    def _predict_cost(self, features: np.ndarray, w: np.ndarray) -> float:
        """Linear regression: bias + X @ w[1:], then rescale."""
        xb = np.concatenate([[1.0], features])
        raw = float(xb @ w) * self._cost_scale
        return max(raw, 25_000.0)

    # ── Feature extraction ───────────────────────────────────────────

    @staticmethod
    def _profile_to_features(profile: UserProfile) -> np.ndarray:
        """Convert a UserProfile into the same 5-feature vector used for training."""
        age_norm    = profile.age / 70.0
        income_norm = profile.income / 3_000_000.0
        dep_norm    = profile.dependents / 5.0
        liab_ratio  = float(np.clip(profile.liability_ratio, 0, 3))
        nw_norm     = float(np.clip(profile.net_worth / 10_000_000.0, -1, 1))
        return np.array([age_norm, income_norm, dep_norm, liab_ratio, nw_norm])

    # ── Public interface ─────────────────────────────────────────────

    def simulate(self, profile: Optional[UserProfile] = None) -> ScenarioSimulationResult:
        """
        Return scenario impacts and total expected loss.

        Uses trained ML models when available; falls back to rule-based
        estimates when models have not been trained yet.
        """
        if profile is None or not self._models_loaded:
            return self._fallback_simulation(profile)

        features = self._profile_to_features(profile)
        breakdown: list[ScenarioBreakdown] = []

        # ── Medical Emergency  (Logistic + Linear Regression) ────────
        med_prob = self._predict_prob(features, self._w_med_prob)
        med_cost = self._predict_cost(features, self._w_med_cost)
        breakdown.append(ScenarioBreakdown(
            scenario_name="medical_emergency",
            probability=round(med_prob, 4),
            cost=round(med_cost, 2),
            expected_impact=round(med_prob * med_cost, 2),
            reasons=self._medical_reasons(profile),
        ))

        # ── Accident  (Logistic + Linear Regression) ─────────────────
        acc_prob = self._predict_prob(features, self._w_acc_prob)
        acc_cost = self._predict_cost(features, self._w_acc_cost)
        breakdown.append(ScenarioBreakdown(
            scenario_name="accident",
            probability=round(acc_prob, 4),
            cost=round(acc_cost, 2),
            expected_impact=round(acc_prob * acc_cost, 2),
            reasons=self._accident_reasons(profile),
        ))

        # ── Income Loss  (Logistic + Linear Regression) ──────────────
        inc_prob = self._predict_prob(features, self._w_inc_prob)
        inc_cost = self._predict_cost(features, self._w_inc_cost)
        breakdown.append(ScenarioBreakdown(
            scenario_name="income_loss",
            probability=round(inc_prob, 4),
            cost=round(inc_cost, 2),
            expected_impact=round(inc_prob * inc_cost, 2),
            reasons=self._income_loss_reasons(profile),
        ))

        expected_loss = round(sum(s.expected_impact for s in breakdown), 2)
        return ScenarioSimulationResult(
            expected_loss=expected_loss,
            scenario_breakdown=breakdown,
        )

    # ── Profile-aware reason generators ────────────────────────────

    @staticmethod
    def _medical_reasons(profile: UserProfile) -> list[str]:
        """Explain in plain language why medical probability is what it is."""
        reasons: list[str] = []

        # Age
        if profile.age > 55:
            reasons.append(f"You are {profile.age} years old — older individuals face significantly higher risk of chronic illness, hospitalisation, and surgery.")
        elif profile.age > 40:
            reasons.append(f"At age {profile.age}, the likelihood of lifestyle diseases like hypertension or diabetes starts to rise.")
        else:
            reasons.append(f"At age {profile.age}, you are relatively young, which lowers your baseline medical risk.")

        # Dependents → elderly parents
        if profile.dependents >= 3:
            reasons.append(f"You have {profile.dependents} dependents. With elderly parents or multiple children in the household, combined medical expenses can be substantially higher.")
        elif profile.dependents > 0:
            reasons.append(f"Supporting {profile.dependents} dependent(s) means medical costs can extend beyond just yourself.")

        # Income → cost scaling
        if profile.income < 400000:
            reasons.append("Your annual income is relatively low, meaning even a moderate medical emergency could consume several months of earnings.")
        elif profile.income > 1500000:
            reasons.append("Higher income individuals often seek premium treatment, which raises the estimated cost of a medical emergency.")

        # Goal signal
        if profile.insurance_goal == "health_security":
            reasons.append("You specifically selected Health Security as your goal, indicating awareness of medical risk — this is factored into the model.")

        return reasons

    @staticmethod
    def _accident_reasons(profile: UserProfile) -> list[str]:
        """Explain in plain language why accident probability is what it is."""
        reasons: list[str] = []

        # Age
        if profile.age < 28:
            reasons.append(f"At age {profile.age}, younger individuals statistically have higher accident rates due to driving behaviour and physical activity.")
        elif profile.age > 55:
            reasons.append(f"At age {profile.age}, reaction times may be slower, which can increase accident risk during commutes.")
        else:
            reasons.append(f"Your age ({profile.age}) places you in a moderate accident-risk bracket.")

        # Car ownership proxy via goal
        if profile.insurance_goal == "car_insurance":
            reasons.append("You are seeking car insurance, which directly implies you own a vehicle — vehicle ownership is the primary driver of accident probability.")

        # Dependents → school runs, more road time
        if profile.dependents >= 2:
            reasons.append(f"With {profile.dependents} dependents, daily commutes for school runs, errands, and family transport increase total time on roads.")

        # Liabilities → vehicle loan proxy
        if profile.liability_ratio > 0.5:
            reasons.append("Your liability-to-income ratio suggests possible vehicle or personal loans, indicating you likely own assets like a car that elevate accident exposure.")

        return reasons

    @staticmethod
    def _income_loss_reasons(profile: UserProfile) -> list[str]:
        """Explain in plain language why income loss probability is what it is."""
        reasons: list[str] = []

        # Liability ratio
        if profile.liability_ratio > 1.0:
            reasons.append(f"Your total liabilities are {profile.liability_ratio:.1f}x your annual income — if you lost your job, EMI payments and debt obligations would be immediately at risk.")
        elif profile.liability_ratio > 0.5:
            reasons.append(f"Your liabilities represent {profile.liability_ratio:.0%} of your income, meaning income disruption would create real financial pressure.")
        else:
            reasons.append("Your liability-to-income ratio is healthy, which lowers the financial severity of a potential income disruption.")

        # Net worth
        if profile.net_worth <= 0:
            reasons.append("Your net worth is currently negative (liabilities exceed assets), meaning you have no financial buffer if income stops.")
        elif profile.net_worth < 500000:
            reasons.append(f"Your net savings cushion of ₹{profile.net_worth:,.0f} could cover only a short period if income stopped unexpectedly.")
        else:
            reasons.append(f"A net worth of ₹{profile.net_worth:,.0f} provides some resilience against income loss.")

        # Dependents
        if profile.dependents >= 2:
            reasons.append(f"With {profile.dependents} dependents relying on your income, any disruption would affect multiple people's daily expenses and education costs.")
        elif profile.dependents == 1:
            reasons.append("One dependent means your income loss would immediately affect another person's financial stability.")

        # Income level
        if profile.income < 300000:
            reasons.append("Low annual income means there is little excess savings each month to fall back on during a period of unemployment.")

        return reasons

    # ── Fallback (rule-based, used only when models are missing) ─────

    def _fallback_simulation(self, profile: Optional[UserProfile] = None) -> ScenarioSimulationResult:
        """Minimal rule-based fallback for backward compatibility."""
        if profile is None:
            static = [
                ("medical_emergency", 0.20, 30_000.0),
                ("accident",          0.10, 50_000.0),
                ("income_loss",       0.05, 100_000.0),
            ]
        else:
            med_p = 0.15 + (0.15 if profile.age > 50 else 0.05 if profile.age > 40 else 0)
            acc_p = 0.10 + (0.05 if profile.age < 30 else 0)
            inc_p = 0.05 + (0.10 if profile.liability_ratio > 1 else 0)
            static = [
                ("medical_emergency", med_p, max(profile.income * 0.05, 25_000)),
                ("accident",          acc_p, max(profile.income * 0.08, 40_000)),
                ("income_loss",       inc_p, profile.income * 1.5),
            ]

        breakdown = [
            ScenarioBreakdown(
                scenario_name=n,
                probability=round(p, 4),
                cost=round(c, 2),
                expected_impact=round(p * c, 2),
            )
            for n, p, c in static
        ]
        expected_loss = round(sum(s.expected_impact for s in breakdown), 2)
        return ScenarioSimulationResult(
            expected_loss=expected_loss,
            scenario_breakdown=breakdown,
        )
