import numpy as np
import json
import os
from typing import List
from app.models import Policy

class NumPyNeuralNetwork:
    """
    A lightweight, pure-NumPy Multi-Layer Perceptron (MLP).
    Demonstrates deep-AI architecture without external library dependencies.
    """
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.1
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.1
        self.b2 = np.zeros(output_dim)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def forward(self, x):
        # Layer 1
        self.z1 = np.dot(x, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)  # Using tanh for hidden layer
        
        # Layer 2
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.probabilities = self.sigmoid(self.z2)
        return self.probabilities

    def save(self, path):
        data = {
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist()
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def load(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                self.W1 = np.array(data["W1"])
                self.b1 = np.array(data["b1"])
                self.W2 = np.array(data["W2"])
                self.b2 = np.array(data["b2"])
            return True
        return False

class RLPolicyAgent:
    """
    Agent that uses a custom-built Neural Network to rank insurance policies.
    """
    def __init__(self, input_dim: int = 5, output_dim: int = 15):
        self.model = NumPyNeuralNetwork(input_dim, 64, output_dim)
        self.model_path = os.path.join("app", "models", "rl_weights.json")
        self.is_trained = self.model.load(self.model_path)

    def get_policy_rankings(self, state: np.ndarray, policies: List[Policy]) -> List[float]:
        """
        Produce a score for each policy using the custom neural network.
        """
        if not self.is_trained:
            # Re-check if model file appeared (e.g. after training)
            if self.model.load(self.model_path):
                self.is_trained = True
            else:
                return [50.0] * len(policies)
            
        # Inference
        probs = self.model.forward(state)
        # Scale 0-1 range to 0-100 for the UI
        scores = probs * 100
        return scores.tolist()
