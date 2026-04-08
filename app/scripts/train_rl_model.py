import numpy as np
import json
import os
import sys

# Add root directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.utils.policy_env import InsuranceEnv
from app.agents.rl_policy_agent import NumPyNeuralNetwork
from app.models import Policy

def train():
    # 1. Load Policies
    policy_path = os.path.join("app", "data", "policies.json")
    with open(policy_path, "r") as f:
        policies_data = json.load(f)
    policies = [Policy(**p) for p in policies_data]
    
    # 2. Setup Env and Model
    env = InsuranceEnv(policies)
    input_dim = 5
    hidden_dim = 64
    output_dim = len(policies)
    nn = NumPyNeuralNetwork(input_dim, hidden_dim, output_dim)
    
    # Hyperparameters
    episodes = 5000
    learning_rate = 0.01
    epsilon = 0.2
    
    print(f"Training NumPy RL Agent (DQN) for {episodes} episodes...")

    
    for ep in range(episodes):
        profile = env.generate_random_user()
        state = env.get_state(profile)
        
        # Forward pass
        probs = nn.forward(state)
        
        # Action selection
        if np.random.rand() < epsilon:
            action_idx = np.random.randint(0, output_dim)
        else:
            action_idx = np.argmax(probs)
            
        # Get Reward
        reward = env.compute_reward(profile, policies[action_idx])
        
        # Target: For our single-step DQN, we want the prediction for action_idx to be the reward
        # (normalized to 0-1 range for the sigmoid output)
        normalized_reward = 1 / (1 + np.exp(-reward/5.0)) # Mapping reward to 0-1 space
        
        # Backpropagation (Manual Gradient Descent)
        # 1. Output error (gradient of loss w.r.t probabilities)
        d_p = probs.copy()
        d_p[action_idx] -= normalized_reward
        
        # 2. Gradient w.r.t z2 and Weights/Biases 2
        # d_z2 = d_p * (probs * (1 - probs)) - Derivative of sigmoid
        d_z2 = d_p * (probs * (1 - probs))
        dW2 = np.outer(nn.a1, d_z2)
        db2 = d_z2
        
        # 3. Gradient w.r.t hidden layer a1 and z1
        # dz1 = np.dot(d_z2, W2.T) * (1 - tanh^2(z1))
        da1 = np.dot(d_z2, nn.W2.T)
        dz1 = da1 * (1 - nn.a1**2)
        dW1 = np.outer(state, dz1)
        db1 = dz1
        
        # 4. Update parameters
        nn.W2 -= learning_rate * dW2
        nn.b2 -= learning_rate * db2
        nn.W1 -= learning_rate * dW1
        nn.b1 -= learning_rate * db1
        
        if (ep + 1) % 1000 == 0:
            loss = np.mean((probs[action_idx] - normalized_reward)**2)
            print(f"Episode {ep+1}/{episodes} | Loss: {loss:.6f} | Reward: {reward:.2f}")

    # 3. Save Model
    model_dir = os.path.join("app", "models")
    os.makedirs(model_dir, exist_ok=True)
    save_path = os.path.join(model_dir, "rl_weights.json")
    nn.save(save_path)
    print(f"Training complete. NumPy weights saved to {save_path}")

if __name__ == "__main__":
    train()
