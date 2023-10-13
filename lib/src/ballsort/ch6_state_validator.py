from dataclasses import dataclass
from ball_control import IllegalBallControlStateError
from state_update_model import (
    StateModel,
)
from state_validator import StateValidator


@dataclass
class Ch6StateValidator(StateValidator):
    """Validates operations"""

    def move_horizontally(self, state: StateModel, distance: int, claw_index: int):
        super().move_horizontally(state=state, distance=distance, claw_index=claw_index)

        newX = state.claws[claw_index].pos.x + distance
        if claw_index == 0 and newX > 2:
            raise IllegalBallControlStateError(f"Horizontal position of claw 0 ({newX}) must be <= 2")
     
        if claw_index == 1 and newX < 2:
            raise IllegalBallControlStateError(f"Horizontal position of claw 1 ({newX}) must be >= 2")