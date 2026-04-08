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
        ))

        # ── Accident  (Logistic + Linear Regression) ─────────────────
        acc_prob = self._predict_prob(features, self._w_acc_prob)
        acc_cost = self._predict_cost(features, self._w_acc_cost)
        breakdown.append(ScenarioBreakdown(
            scenario_name="accident",
            probability=round(acc_prob, 4),
            cost=round(acc_cost, 2),
            expected_impact=round(acc_prob * acc_cost, 2),
        ))

        # ── Income Loss  (Logistic + Linear Regression) ──────────────
        inc_prob = self._predict_prob(features, self._w_inc_prob)
        inc_cost = self._predict_cost(features, self._w_inc_cost)
        breakdown.append(ScenarioBreakdown(
            scenario_name="income_loss",
            probability=round(inc_prob, 4),
            cost=round(inc_cost, 2),
            expected_impact=round(inc_prob * inc_cost, 2),
        ))

        expected_loss = round(sum(s.expected_impact for s in breakdown), 2)
        return ScenarioSimulationResult(
            expected_loss=expected_loss,
            scenario_breakdown=breakdown,
        )

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
