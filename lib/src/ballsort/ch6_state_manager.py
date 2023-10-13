from dataclasses import dataclass
from ch6_state_validator import Ch6StateValidator
from scenario import Scenario

from state_manager import StateManager

@dataclass
class Ch6StateManager(StateManager):
    """Validates operations and keeps state up to date"""

    def __init__(self, scenario : Scenario | None = None):
        super().__init__(scenario=scenario)
        self.validator = Ch6StateValidator()
