# AI Technical Guide: NumPy-Based Reinforcement Learning

This project incorporates a custom-built **Reinforcement Learning (RL)** system to handle insurance policy selection. Unlike standard rule-based systems, this agent learns from simulated data to optimize for user suitability and financial health.

## 🧠 Model Architecture: Deep Q-Network (DQN)

The agent uses a **Deep Q-Network** implemented from scratch using **pure NumPy**. This approach was chosen to demonstrate a deep understanding of the mathematical foundations of AI (backpropagation, activation functions, and gradient descent) without relying on heavy external frameworks.

- **Input Layer (State)**: 5 Neurons
    - Age (Normalized)
    - Income (Normalized)
    - Dependents (Normalized)
    - Net Worth (Normalized)
    - Risk Score (Normalized)
- **Hidden Layer**: 64 Neurons with **Tanh** activation.
- **Output Layer (Actions)**: 15 Neurons (One for each insurance policy).
- **Activation**: **Sigmoid** activation on the output to map values to a 0–1 confidence range.

## 🎮 The Training Environment (`InsuranceEnv`)

We built a custom simulator that generates thousands of synthetic user profiles. For every action the agent takes (selecting a policy), the environment provides a **Reward**:

- **+10.0**: Selection matches the user's primary insurance goal.
- **-10.0**: Premium exceeds the user's calculated budget (6% of income).
- **+8.0**: Coverage is within 80-150% of the recommended "10x Income" target.
- **-5.0**: Selection leaves the user severely under-insured.

## 📉 Training Process (Backpropagation)

The model is trained over **5,000 episodes** using **Manual Gradient Descent**:

1.  **Forward Pass**: Calculate the predicted "match score" for each policy.
2.  **Exploration (Epsilon-Greedy)**: 20% of the time, the agent picks a random policy to "explore" new possibilities; 80% of the time, it "exploits" its learned knowledge.
3.  **Loss Calculation**: Computes the Mean Squared Error (MSE) between the predicted score and the actual reward received.
4.  **Backward Pass**: Calculate gradients for every weight and bias using the chain rule.
5.  **Optimizer**: Updates weights using a learning rate of `0.01`.

## 🚀 Why this is "Real AI"
By moving away from "if-else" logic, the system now has the capacity to:
- **Generalize**: It can make predictions for user profiles it has never seen before.
- **Optimize**: It maximizes a multi-dimensional reward function (balancing cost vs. protection).
- **Self-Improve**: The training script (`train_rl_model.py`) can be re-run with new data to continuously improve the agent's performance.

---

# Data-Driven Scenario Calibration (ML Component 2)

The **Scenario Simulation Agent** has been upgraded from hard-coded rules to a fully **data-driven** system powered by trained Logistic and Linear Regression models.

## 📊 Training Data

A synthetic actuarial dataset of **3,000 samples** is generated (`generate_scenario_data.py`), where each record represents a person with:

| Feature | Description | Normalisation |
|---|---|---|
| `age_norm` | Person's age | `age / 70` |
| `income_norm` | Annual income | `income / 3,000,000` |
| `dep_norm` | Number of dependents | `dependents / 5` |
| `liab_ratio` | Liabilities ÷ Income | Clipped 0–3 |
| `nw_norm` | Net worth | Clipped -1 to 1 |

Ground-truth labels (whether the person experienced a medical emergency, accident, or income loss) are generated using **sigmoid-over-logit** functions that mimic real-world actuarial distributions.

## 🧮 Models Trained (6 total)

### Probability Models — Logistic Regression (Gradient Descent)

For each scenario (medical, accident, income loss), a Logistic Regression model is trained using **Binary Cross-Entropy** loss and **Gradient Descent**:

```
P(event) = sigmoid(bias + w1*age + w2*income + w3*deps + w4*liab_ratio + w5*net_worth)
```

Training loop (500–600 epochs):
1. Forward pass: compute `p = sigmoid(X @ w)`
2. Gradient: `grad = X.T @ (p - y) / n`
3. Update: `w -= learning_rate * grad`

### Cost Models — Linear Regression (Closed-Form OLS)

For each scenario, a Linear Regression model predicts the expected cost using the **exact analytical solution**:

```
w = (X^T X)^(-1) X^T y
```

This is a **zero-iteration** solution — no gradient descent needed. Cost predictions are scaled by 1,000,000 for numerical stability.

## 📈 Model Performance

| Model | Type | Metric | Score |
|---|---|---|---|
| Medical Probability | Logistic Regression | Accuracy | 61.5% |
| Accident Probability | Logistic Regression | Accuracy | 90.6% |
| Income Loss Probability | Logistic Regression | Accuracy | 82.0% |
| Medical Cost | Linear Regression | RMSE | 0.032 |
| Accident Cost | Linear Regression | RMSE | 0.050 |
| Income Loss Cost | Linear Regression | RMSE | 0.655 |

## 🔄 How It Works at Runtime

1. User profile is converted to a 5-feature vector (same normalisation as training)
2. Feature vector is fed through the Logistic Regression model → predicts **probability** (0–60%)
3. Feature vector is fed through the Linear Regression model → predicts **expected cost** (₹)
4. `Expected Impact = Probability × Cost` for each scenario
5. `Total Expected Loss = Sum of all impacts`

## 🗂 Files

| File | Purpose |
|---|---|
| `app/scripts/generate_scenario_data.py` | Generates synthetic actuarial training data |
| `app/scripts/train_scenario_models.py` | Trains all 6 models and saves weights |
| `app/models/scenario_models.json` | Saved model weights (Logistic + Linear) |
| `app/agents/scenario_simulation.py` | Agent that loads and uses the trained models |
