from dataclasses import dataclass
from ch8_state_validator import Ch8StateValidator
from scenario import Scenario

from state_manager import StateManager

@dataclass
class Ch8StateManager(StateManager):
    """Validates operations and keeps state up to date"""

    def __init__(self, scenario : Scenario | None = None):
        super().__init__(scenario=scenario)
        self.validator = Ch8StateValidator()
