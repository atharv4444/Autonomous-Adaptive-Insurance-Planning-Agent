import random
import numpy as np
from typing import List, Tuple
from app.models import UserProfile, Policy, UserInput
from app.agents.user_profiling import UserProfilingAgent
from app.agents.risk_analysis import RiskAnalysisAgent

class InsuranceEnv:
    """
    A simulation environment for training RL agents in policy selection.
    """
    def __init__(self, policies: List[Policy]):
        self.policies = policies
        self.profiler = UserProfilingAgent()
        self.risk_agent = RiskAnalysisAgent()
        
    def generate_random_user(self) -> UserProfile:
        """Create a diverse synthetic user profile."""
        u_input = UserInput(
            age=random.randint(18, 65),
            income=random.uniform(200000, 3000000),
            dependents=random.randint(0, 5),
            assets=random.uniform(0, 10000000),
            liabilities=random.uniform(0, 5000000),
            insurance_goal=random.choice(["family_protection", "health_security", "wealth_protection"])
        )
        return self.profiler.build_profile(u_input)

    def get_state(self, profile: UserProfile) -> np.ndarray:
        """Vectorize a user profile into a state tensor for the RL model."""
        # Normalize values roughly to keep inputs stable for the NN
        state = [
            profile.age / 70.0,
            profile.income / 3000000.0,
            profile.dependents / 5.0,
            profile.net_worth / 10000000.0,
            # We'll calculate a baseline risk score for the state
            self.risk_agent.calculate_risk(profile)[0] / 100.0
        ]
        return np.array(state, dtype=np.float32)

    def compute_reward(self, profile: UserProfile, policy: Policy) -> float:
        """
        Calculate the reward for selecting a specific policy for a user.
        Reward is higher if the policy fits the profile goals and budget.
        """
        reward = 0.0
        
        # 1. Goal Alignment
        if profile.insurance_goal in policy.target_profile:
            reward += 10.0
        else:
            reward -= 5.0
            
        # 2. Affordability (Budget approx 6% of income)
        budget = profile.income * 0.06
        if policy.premium <= budget:
            reward += 5.0
        else:
            # Harsh penalty for overspending
            reward -= 10.0 * (policy.premium / budget)

        # 3. Coverage Fit (Recommended 10x income)
        target_coverage = profile.income * 10
        coverage_ratio = policy.coverage / target_coverage if target_coverage > 0 else 1.0
        if 0.8 <= coverage_ratio <= 1.5:
            reward += 8.0
        elif coverage_ratio < 0.5:
            reward -= 5.0 # Underinsured
            
        return reward
