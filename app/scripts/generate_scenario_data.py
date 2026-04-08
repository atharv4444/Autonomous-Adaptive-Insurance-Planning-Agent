"""
Generate synthetic historical insurance claims dataset for scenario calibration.

Features (X):  age, income_norm, dependents, liability_ratio, net_worth_norm
Labels  (y):   had_medical (0/1), had_accident (0/1), had_income_loss (0/1)
Costs   (c):   medical_cost, accident_cost, income_loss_cost (for regression)
"""

import numpy as np
import json
import os
import sys
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))


def generate_dataset(n_samples: int = 3000, seed: int = 42) -> dict:
    """
    Produce a dict of NumPy arrays representing a realistic synthetic
    insurance claims population.

    Ground-truth probabilities are derived from epidemiological heuristics
    that closely mirror Indian insurance actuarial baselines.
    """
    rng = np.random.default_rng(seed)

    age           = rng.integers(18, 70, n_samples).astype(float)
    income        = rng.uniform(200_000, 3_000_000, n_samples)
    dependents    = rng.integers(0, 6, n_samples).astype(float)
    liabilities   = rng.uniform(0, 5_000_000, n_samples)
    assets        = rng.uniform(0, 10_000_000, n_samples)
    net_worth     = assets - liabilities

    # Derived actuarial features (same normalisation used at inference)
    age_norm      = age / 70.0
    income_norm   = income / 3_000_000.0
    dep_norm      = dependents / 5.0
    liab_ratio    = np.clip(liabilities / np.maximum(income, 1), 0, 3)
    nw_norm       = np.clip(net_worth / 10_000_000.0, -1, 1)

    # ── Medical Emergency ──────────────────────────────────────────────
    # Older, more dependents, lower income → higher medical probability
    logit_med = (
        -1.8
        + 1.8 * age_norm
        + 0.6 * dep_norm
        - 0.5 * income_norm
        + 0.3 * liab_ratio
    )
    p_med = _sigmoid(logit_med)
    had_medical = rng.binomial(1, p_med).astype(float)

    # Base cost: 5 % of income, scaled by age; add noise
    med_cost = (income * 0.05) * (1 + 0.8 * age_norm) * rng.uniform(0.7, 1.5, n_samples)
    med_cost = np.maximum(med_cost, 25_000)

    # ── Accident ──────────────────────────────────────────────────────
    # Younger, more dependents → higher accident probability
    logit_acc = (
        -2.0
        - 0.8 * age_norm          # younger = higher risk
        + 0.4 * dep_norm
    )
    p_acc = _sigmoid(logit_acc)
    had_accident = rng.binomial(1, p_acc).astype(float)

    acc_cost = (income * 0.08) * (1 + 0.4 * dep_norm) * rng.uniform(0.6, 1.6, n_samples)
    acc_cost = np.maximum(acc_cost, 40_000)

    # ── Income Loss ───────────────────────────────────────────────────
    # High liabilities, low net worth → much higher income-loss risk
    logit_inc = (
        -3.0
        + 2.0 * liab_ratio
        - 1.0 * nw_norm
        + 0.5 * dep_norm
    )
    p_inc = _sigmoid(logit_inc)
    had_income_loss = rng.binomial(1, p_inc).astype(float)

    inc_multiplier = 1.5 + 0.5 * dep_norm + 0.4 * liab_ratio
    inc_cost = income * inc_multiplier * rng.uniform(0.8, 1.3, n_samples)

    # ── Pack into a serialisable dict ────────────────────────────────
    X = np.column_stack([age_norm, income_norm, dep_norm, liab_ratio, nw_norm])

    dataset = {
        "X":              X.tolist(),
        "had_medical":    had_medical.tolist(),
        "had_accident":   had_accident.tolist(),
        "had_income_loss": had_income_loss.tolist(),
        "med_cost":       med_cost.tolist(),
        "acc_cost":       acc_cost.tolist(),
        "inc_cost":       inc_cost.tolist(),
        "n_samples":      n_samples,
        "feature_names":  ["age_norm", "income_norm", "dep_norm", "liab_ratio", "nw_norm"],
    }
    return dataset


if __name__ == "__main__":
    dataset = generate_dataset(n_samples=3000)
    out_path = os.path.join("app", "data", "scenario_training_data.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(dataset, f)
    print(f"Generated {dataset['n_samples']} synthetic samples -> {out_path}")
