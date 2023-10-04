from dataclasses import dataclass
from ch4_state_validator import Ch4StateValidator
from scenario import Scenario

from state_manager import StateManager

@dataclass
class Ch4StateManager(StateManager):
    """Validates operations and keeps state up to date"""

    def __init__(self, scenario : Scenario | None = None):
        super().__init__(scenario=scenario)
        self.validator = Ch4StateValidator()
