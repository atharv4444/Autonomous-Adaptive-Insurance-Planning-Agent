"""
Adaptive Learner Agent — enables the system to learn from its mistakes in real-time.
This agent acts as a supervisor that translates feedback into architectural updates.
"""

from __future__ import annotations
import os
import numpy as np
from typing import List, Optional, Dict, Any
from app.models import UserProfile, Policy, RankedPolicy, CriticResult
from app.agents.rl_policy_agent import RLPolicyAgent
from app.utils.policy_env import InsuranceEnv

class AdaptiveLearnerAgent:
    """
    Orchestrates the 'learning' process by identifying mistakes and correcting the model.
    It closes the loop between agent execution and model evolution.
    """

    def __init__(self, rl_agent: RLPolicyAgent):
        self.rl_agent = rl_agent
        # Reuse the environment helper for reward logic
        self.env = InsuranceEnv(policies=[]) 

    def learn_from_critic(
        self, 
        profile: UserProfile, 
        policies: List[Policy], 
        initial_ranking: List[RankedPolicy], 
        critic_result: CriticResult,
        risk_score: float
    ) -> Dict[str, Any]:
        """
        Learns from a 'mistake' identified by the Critic.
        If the Critic reranked the policy, we penalize the top initial choice
        and reward the validated choice.
        """
        # Vectorize state
        state = np.array([
            profile.age / 70.0,
            profile.income / 3000000.0,
            profile.dependents / 5.0,
            profile.net_worth / 10000000.0,
            risk_score / 100.0
        ], dtype=np.float32)

        # Identify which policy was actually recommended by the system (Action)
        recommended_policy = initial_ranking[0].policy
        validated_policy = critic_result.validated_policy.policy
        
        # Find indices
        recommended_idx = -1
        validated_idx = -1
        for i, p in enumerate(policies):
            if p.policy_name == recommended_policy.policy_name:
                recommended_idx = i
            if p.policy_name == validated_policy.policy_name:
                validated_idx = i

        results = {"learned": False, "loss": 0.0}

        # If a rerank happened, it's a 'mistake' signal
        if recommended_policy.policy_name != validated_policy.policy_name:
            # Reward the validated choice
            reward = self.env.compute_reward(profile, validated_policy)
            loss_validated = self.rl_agent.model.update(state, validated_idx, reward)
            
            # Penalize the initial mistake (negative reward)
            loss_penalty = self.rl_agent.model.update(state, recommended_idx, -5.0)
            
            # Save the new knowledge
            self.rl_agent.model.save(self.rl_agent.model_path)
            
            results["learned"] = True
            results["loss"] = (loss_validated + loss_penalty) / 2
            results["message"] = f"Learned from critic rerank: Penalized {recommended_policy.policy_name}, Rewarded {validated_policy.policy_name}"
        
        elif len(critic_result.issues) > 0 and "No major issues" not in critic_result.issues[0]:
            # Even if no rerank, if there are issues, we can learn to diminish the score of this match
            reward = self.env.compute_reward(profile, validated_policy) - 2.0 # Apply penalty for issues
            loss = self.rl_agent.model.update(state, validated_idx, reward)
            self.rl_agent.model.save(self.rl_agent.model_path)
            results["learned"] = True
            results["loss"] = loss
            results["message"] = f"Adaptive update: Slightly penalized {validated_policy.policy_name} due to critic issues: {critic_result.issues[0]}"

        return results
