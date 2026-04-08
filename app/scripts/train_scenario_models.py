"""
Train NumPy-based models for scenario probability and cost calibration.

Models trained:
  Logistic Regression  →  P(medical), P(accident), P(income_loss)
  Linear   Regression  →  E[med_cost], E[acc_cost], E[inc_cost]

Weights are saved to app/models/scenario_models.json
"""

import numpy as np
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from app.scripts.generate_scenario_data import generate_dataset


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -30, 30)))


def add_bias(X: np.ndarray) -> np.ndarray:
    """Prepend a ones column for the bias term."""
    return np.hstack([np.ones((X.shape[0], 1)), X])


# ─── Logistic Regression (Binary Cross-Entropy, Gradient Descent) ─────────────

def train_logistic(X: np.ndarray, y: np.ndarray,
                   lr: float = 0.1, epochs: int = 500) -> np.ndarray:
    """Return weight vector (including bias) trained with gradient descent."""
    Xb = add_bias(X)
    w = np.zeros(Xb.shape[1])
    n = len(y)
    for epoch in range(epochs):
        p = _sigmoid(Xb @ w)
        grad = Xb.T @ (p - y) / n
        w -= lr * grad
    return w


def predict_logistic(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    return _sigmoid(add_bias(X) @ w)


# ─── Linear Regression (OLS closed form: w = (XᵀX)⁻¹ Xᵀy) ─────────────────

def train_linear(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Ordinary Least Squares — exact solution in one step."""
    Xb = add_bias(X)
    # Numerically stable via pseudo-inverse
    w = np.linalg.pinv(Xb.T @ Xb) @ Xb.T @ y
    return w


def predict_linear(X: np.ndarray, w: np.ndarray) -> np.ndarray:
    return add_bias(X) @ w


# ─── Evaluation ──────────────────────────────────────────────────────────────

def accuracy(y_true, y_pred_prob, threshold=0.5):
    y_hat = (y_pred_prob >= threshold).astype(float)
    return float(np.mean(y_hat == y_true))


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


# ─── Main ─────────────────────────────────────────────────────────────────────

def train():
    print("Generating synthetic historical claims dataset (3,000 samples)...")
    data = generate_dataset(n_samples=3000)

    X            = np.array(data["X"])
    y_med        = np.array(data["had_medical"])
    y_acc        = np.array(data["had_accident"])
    y_inc        = np.array(data["had_income_loss"])
    c_med        = np.array(data["med_cost"])
    c_acc        = np.array(data["acc_cost"])
    c_inc        = np.array(data["inc_cost"])

    # Normalise cost targets (helps linear regression converge)
    c_med_norm   = c_med  / 1_000_000.0
    c_acc_norm   = c_acc  / 1_000_000.0
    c_inc_norm   = c_inc  / 1_000_000.0

    print("Training Logistic Regression for medical probability...")
    w_med_prob   = train_logistic(X, y_med, lr=0.2, epochs=600)
    print(f"  Accuracy: {accuracy(y_med, predict_logistic(X, w_med_prob)):.2%}")

    print("Training Logistic Regression for accident probability...")
    w_acc_prob   = train_logistic(X, y_acc, lr=0.2, epochs=600)
    print(f"  Accuracy: {accuracy(y_acc, predict_logistic(X, w_acc_prob)):.2%}")

    print("Training Logistic Regression for income-loss probability...")
    w_inc_prob   = train_logistic(X, y_inc, lr=0.2, epochs=600)
    print(f"  Accuracy: {accuracy(y_inc, predict_logistic(X, w_inc_prob)):.2%}")

    print("Training Linear Regression for medical cost...")
    w_med_cost   = train_linear(X, c_med_norm)
    print(f"  RMSE: {rmse(c_med_norm, predict_linear(X, w_med_cost)):.4f}")

    print("Training Linear Regression for accident cost...")
    w_acc_cost   = train_linear(X, c_acc_norm)
    print(f"  RMSE: {rmse(c_acc_norm, predict_linear(X, w_acc_cost)):.4f}")

    print("Training Linear Regression for income-loss cost...")
    w_inc_cost   = train_linear(X, c_inc_norm)
    print(f"  RMSE: {rmse(c_inc_norm, predict_linear(X, w_inc_cost)):.4f}")

    models = {
        "med_prob_weights":  w_med_prob.tolist(),
        "acc_prob_weights":  w_acc_prob.tolist(),
        "inc_prob_weights":  w_inc_prob.tolist(),
        "med_cost_weights":  w_med_cost.tolist(),
        "acc_cost_weights":  w_acc_cost.tolist(),
        "inc_cost_weights":  w_inc_cost.tolist(),
        "cost_scale":        1_000_000.0,
        "feature_names":     data["feature_names"],
    }

    model_dir  = os.path.join("app", "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "scenario_models.json")
    with open(model_path, "w") as f:
        json.dump(models, f, indent=2)

    print(f"All 6 models saved to {model_path}")


if __name__ == "__main__":
    train()
