"""Central execution orchestrator."""

import time
from typing import Dict, Any, List

from app.core.shared_memory import SharedMemory
from app.core.plan import Plan
from app.core.tools import (
    ProfileUserTool, CalculateRiskTool, SimulateScenarioTool,
    EvaluatePoliciesTool, ValidateCriticTool, LearnAdaptiveTool,
    CheckComplianceTool, PersistMemoryTool
)
from app.agents.goal_planner import GoalPlannerAgent
from app.models import AgentTraceEntry

class OrchestratorAgent:
    """
    Main orchestration engine.
    Continuously processes the plan until completion.
    """
    def __init__(self):
        self.memory = SharedMemory()
        
        # Instantiate tools
        eval_tool = EvaluatePoliciesTool()
        self.tools = {
            "ProfileUserTool": ProfileUserTool(),
            "CalculateRiskTool": CalculateRiskTool(),
            "SimulateScenarioTool": SimulateScenarioTool(),
            "EvaluatePoliciesTool": eval_tool,
            "ValidateCriticTool": ValidateCriticTool(),
            "LearnAdaptiveTool": LearnAdaptiveTool(eval_tool.agent.rl_agent),
            "CheckComplianceTool": CheckComplianceTool(),
            "PersistMemoryTool": PersistMemoryTool()
        }
        
        self.planner = GoalPlannerAgent()
        self.trace: List[AgentTraceEntry] = []

    def run_loop(self, user_input) -> Dict[str, Any]:
        """
        Main execution loop.
        """
        self.memory.clear()
        self.memory.set("user_input", user_input)
        
        # 1. Generate initial plan
        plan = self.planner.generate_plan()
        self.memory.set("current_plan", plan)
        goal_achieved = False
        replanning_count = 0
        
        while not goal_achieved and replanning_count < 3:
            current_step = plan.get_next_step()
            
            if current_step is None:
                # Reached end of plan
                goal_achieved = True
                break
                
            tool = self.tools.get(current_step)
            if not tool:
                raise ValueError(f"Unknown Tool / Action requested: {current_step}")
            
            # Execute action
            t0 = time.perf_counter()
            result = tool.execute(self.memory)
            duration = round((time.perf_counter() - t0) * 1000, 2)
            
            # Update trace log
            self.trace.append(AgentTraceEntry(
                agent_name=tool.name,
                input_summary=f"Running tool: {tool.name}",
                output_summary=f"Result: {result.get('status')} - details in memory",
                duration_ms=duration
            ))

            # Check for replanning signal
            if result.get("action") == "replanning_required":
                replanning_count += 1
                new_steps = self.planner.revise_plan_on_rejection()
                plan.revise_plan(new_steps)
                self.trace.append(AgentTraceEntry(
                    agent_name="GoalPlannerAgent",
                    input_summary="Critic rejection detected",
                    output_summary=f"Revised plan due to suboptimal output (Replans: {replanning_count})",
                    duration_ms=0.0
                ))
                continue
            
            plan.mark_step_complete()
            
        # Pass context back to caller
        return self._build_final_response()
        
    def _build_final_response(self) -> Dict[str, Any]:
        """Format shared memory into response dictionary."""
        return {
            "user_profile": self.memory.get("user_profile"),
            "risk_score": self.memory.get("risk_score"),
            "risk_label": self.memory.get("risk_label"),
            "expected_loss": self.memory.get("expected_loss"),
            "scenario_result": self.memory.get("scenario_result"),
            "best_policy": self.memory.get("best_policy"),
            "top_policies": self.memory.get("ranked_policies")[:3] if self.memory.get("ranked_policies") else [],
            "critic_result": self.memory.get("critic_result"),
            "compliance_report": self.memory.get("compliance_report"),
            "memory_snapshot": self.memory.get("memory_snapshot"),
            "learning_results": self.memory.get("learning_results"),
            "trace": self.trace
        }
