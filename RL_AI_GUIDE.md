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
