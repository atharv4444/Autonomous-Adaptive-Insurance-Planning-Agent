"""Plan management for dynamic agent loops."""

from typing import List, Optional

class Plan:
    """
    Execution plan. List of tools to run.
    """
    def __init__(self, steps: List[str] = None):
        self.steps = steps or []
        self.current_step_index = 0
        self.history: List[str] = []

    def get_next_step(self) -> Optional[str]:
        """Get next step."""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def mark_step_complete(self) -> None:
        """Complete current step."""
        if self.current_step_index < len(self.steps):
            completed = self.steps[self.current_step_index]
            self.history.append(completed)
            self.current_step_index += 1

    def revise_plan(self, new_steps: List[str]) -> None:
        """
        Overwrite remaining steps.
        """
        self.steps = self.history + new_steps
        # current index stays the same (pointing to the start of new_steps)

    def prepend_step(self, step: str) -> None:
        """Add step here."""
        self.steps.insert(self.current_step_index, step)

    def is_complete(self) -> bool:
        return self.current_step_index >= len(self.steps)
