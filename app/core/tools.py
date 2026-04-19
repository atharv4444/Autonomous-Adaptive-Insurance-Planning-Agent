"""Tool abstraction wrappers."""

from abc import ABC, abstractmethod
from typing import Any, Dict

# Import agents
from app.agents.user_profiling import UserProfilingAgent
from app.agents.risk_analysis import RiskAnalysisAgent
from app.agents.scenario_simulation import ScenarioSimulationAgent
from app.agents.policy_evaluation import PolicyEvaluationAgent
from app.agents.critic import CriticAgent
from app.agents.adaptive_learner import AdaptiveLearnerAgent
from app.memory.memory_store import MemoryStore
from app.utils.helpers import load_policies
from app.utils.irdai_compliance import IRDAIComplianceChecker

class BaseTool(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, external_memory: "SharedMemory") -> Dict[str, Any]:
        """Execute tool logic using shared memory state."""
        pass


class ProfileUserTool(BaseTool):
    name = "ProfileUserTool"
    description = "Builds user profile."
    
    def __init__(self):
        self.agent = UserProfilingAgent()

    def execute(self, memory) -> Dict[str, Any]:
        user_input = memory.get("user_input")
        if not user_input:
            raise ValueError("user_input not found in memory")
        
        profile = self.agent.build_profile(user_input)
        memory.set("user_profile", profile)
        return {"status": "success", "profile": profile}

class CalculateRiskTool(BaseTool):
    name = "CalculateRiskTool"
    description = "Computes risk score."

    def __init__(self):
        self.agent = RiskAnalysisAgent()

    def execute(self, memory) -> Dict[str, Any]:
        profile = memory.get("user_profile")
        risk_score, risk_label = self.agent.calculate_risk(profile)
        memory.set("risk_score", risk_score)
        memory.set("risk_label", risk_label)
        return {"status": "success", "risk_label": risk_label}

class SimulateScenarioTool(BaseTool):
    name = "SimulateScenarioTool"
    description = "Runs loss simulation."

    def __init__(self):
        self.agent = ScenarioSimulationAgent()

    def execute(self, memory) -> Dict[str, Any]:
        profile = memory.get("user_profile")
        result = self.agent.simulate(profile)
        memory.set("scenario_result", result)
        memory.set("expected_loss", result.expected_loss)
        return {"status": "success", "expected_loss": result.expected_loss}

class EvaluatePoliciesTool(BaseTool):
    name = "EvaluatePoliciesTool"
    description = "Scores and ranks policies."

    def __init__(self):
        self.agent = PolicyEvaluationAgent()

    def execute(self, memory) -> Dict[str, Any]:
        profile = memory.get("user_profile")
        risk_score = memory.get("risk_score")
        risk_label = memory.get("risk_label")
        expected_loss = memory.get("expected_loss")
        
        policies = load_policies()
        memory.set("raw_policies", policies)

        ranked = self.agent.rank_policies(
            profile=profile,
            policies=policies,
            risk_score=risk_score,
            risk_label=risk_label,
            expected_loss=expected_loss
        )
        memory.set("ranked_policies", ranked)
        return {"status": "success", "top_policy": ranked[0].policy.policy_name if ranked else None}

class PersistMemoryTool(BaseTool):
    name = "PersistMemoryTool"
    description = "Persists profile and recommendation."
    
    def __init__(self):
        self.store = MemoryStore()

    def execute(self, memory) -> Dict[str, Any]:
        profile = memory.get("user_profile")
        best_policy = memory.get("best_policy")
        
        signature = self.store.save_user_profile(profile)
        self.store.save_recommendation(signature, best_policy)
        
        snapshot = {
            "profile_signature": signature,
            "previous_recommendations": self.store.get_previous_recommendations(limit=3),
        }
        memory.set("memory_snapshot", snapshot)
        return {"status": "success", "saved": True}


class CheckComplianceTool(BaseTool):
    name = "CheckComplianceTool"
    description = "Runs compliance checks."

    def __init__(self):
        self.checker = IRDAIComplianceChecker()

    def execute(self, memory) -> Dict[str, Any]:
        profile = memory.get("user_profile")
        best_policy = memory.get("best_policy")
        
        report = self.checker.check_compliance(profile, best_policy)
        memory.set("compliance_report", report)
        
        if not report["is_compliant"]:
            # Returns warning on compliance issue.
            return {"status": "warning", "issues": report["issues"]}
        
        return {"status": "success"}


class ValidateCriticTool(BaseTool):
    name = "ValidateCriticTool"
    description = "Validates top policy match."

    def __init__(self):
        self.agent = CriticAgent()

    def execute(self, memory) -> Dict[str, Any]:
        ranked = memory.get("ranked_policies")
        profile = memory.get("user_profile")
        risk_label = memory.get("risk_label")
        expected_loss = memory.get("expected_loss")
        
        result = self.agent.validate(ranked, profile, risk_label, expected_loss)
        
        memory.set("best_policy", result.validated_policy)
        memory.set("critic_result", result)

        if result.requires_replanning:
            return {"status": "failure", "message": "Critic triggered re-planning", "action": "replanning_required"}
        
        return {"status": "success", "confidence": result.confidence_score}


class LearnAdaptiveTool(BaseTool):
    name = "LearnAdaptiveTool"
    description = "Triggers RL model update."

    def __init__(self, rl_agent):
        self.agent = AdaptiveLearnerAgent(rl_agent)

    def execute(self, memory) -> Dict[str, Any]:
        profile = memory.get("user_profile")
        policies = memory.get("raw_policies")
        ranked = memory.get("ranked_policies")
        critic_result = memory.get("critic_result")
        risk_score = memory.get("risk_score")

        learning_results = self.agent.learn_from_critic(
            profile=profile,
            policies=policies,
            initial_ranking=ranked,
            critic_result=critic_result,
            risk_score=risk_score
        )
        
        memory.set("learning_results", learning_results)
        return {"status": "success", "learned": learning_results["learned"]}
