from dataclasses import dataclass
from ball_control import IllegalBallControlStateError
from state_utils import (
    get_top_occupied_index,
    get_top_vacant_index,
    is_ball_at_current_pos,
    is_ball_in_claw,
)
from state_update_model import (
    StateModel,
    MIN_X,
    MIN_Y,
)


@dataclass
class StateValidator:
    """Validates operations"""

    def move_horizontally(self, state: StateModel, distance: int):
        if (state.moving_horizontally):
            raise IllegalBallControlStateError("Already moving horizontally")
        
        newX = state.claw.pos.x + distance
        if newX < MIN_X or newX > state.max_x:
            raise IllegalBallControlStateError(f"X coordinate out of bounds x={newX} minX={MIN_X} maxX={state.max_x}")
    
    def move_vertically(self, state: StateModel, distance: int) -> None:
        if (state.moving_vertically):
            raise IllegalBallControlStateError("Already moving vertically")
        
        newY = state.claw.pos.y + distance
        if newY < MIN_Y or newY > state.max_y:
            raise IllegalBallControlStateError(f"Y coordinate out of bounds y={newY} minY={MIN_Y} maxY={state.max_y}")

    def _check_claw_for_ongoing_operations(self, state: StateModel):
        if (state.operating_claw):
            raise IllegalBallControlStateError("Claw already opening or closing")
        
        if (state.moving_horizontally or state.moving_vertically):
            raise IllegalBallControlStateError("Marble dropped while claw is in motion")

    def open_claw(self, state: StateModel):
        #print("state: ", state)
        if not is_ball_in_claw(state):
            return
        
        self._check_claw_for_ongoing_operations(state=state)

        if state.claw.pos.y != get_top_vacant_index(state):
            raise IllegalBallControlStateError(
                f"Illegal drop location. Must be topmost vacant position ({get_top_vacant_index(state)}). Y={state.claw.pos.y}."
            )

    def close_claw(self, state: StateModel):
        #print("state: ", state)
        if not is_ball_at_current_pos(state):
            return
        
        self._check_claw_for_ongoing_operations(state=state)

        if state.claw.pos.y != get_top_occupied_index(state):
            raise IllegalBallControlStateError(
                f"Illegal grab. Must be topmost marble position ({get_top_occupied_index(state)}). Y={state.claw.pos.y}."
            )
