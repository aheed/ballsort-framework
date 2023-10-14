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

    def _check_claw_index(self, state: StateModel, claw_index:int):
        if not claw_index < len(state.claws):
            raise IndexError("Claw index out of bounds")

    def _check_claw_collision(self, state: StateModel, claw_index: int, x: int):
        if len(state.claws) > claw_index+1:
            compare_index = claw_index+1
            compare_x = state.claws[compare_index].pos.x
            #print(f"horizontal position of claw {claw_index} ({x}) must be < horizontal position of claw {compare_index} ({compare_x})")
            if x >= compare_x:
                raise IllegalBallControlStateError(f"horizontal position of claw {claw_index} ({x}) must be < horizontal position of claw {compare_index} ({compare_x})")

        if claw_index > 0:
            compare_index = claw_index-1
            compare_x = state.claws[compare_index].pos.x
            #print(f"horizontal position of claw {claw_index} ({x}) must be > horizontal position of claw {compare_index} ({compare_x})")
            if x <= compare_x:
                raise IllegalBallControlStateError(f"horizontal position of claw {claw_index} ({x}) must be > horizontal position of claw {compare_index} ({compare_x})")

    def move_horizontally(self, state: StateModel, distance: int, claw_index: int):
        self._check_claw_index(state=state, claw_index=claw_index)
        
        claw = state.claws[claw_index]

        if (claw.moving_horizontally):
            raise IllegalBallControlStateError("Already moving horizontally")
        
        newX = claw.pos.x + distance
        min_x = max(MIN_X, claw.min_x)
        max_x = min(state.max_x, claw.max_x)
        if newX < min_x or newX > max_x:
            raise IllegalBallControlStateError(f"X coordinate out of bounds x={newX} minX={min_x} maxX={max_x}")
        self._check_claw_collision(state=state, claw_index=claw_index, x=newX)
    
    def move_vertically(self, state: StateModel, distance: int, claw_index: int) -> None:
        self._check_claw_index(state=state, claw_index=claw_index)

        if (state.claws[claw_index].moving_vertically):
            raise IllegalBallControlStateError("Already moving vertically")
        
        newY = state.claws[claw_index].pos.y + distance
        if newY < MIN_Y or newY > state.max_y:
            raise IllegalBallControlStateError(f"Y coordinate out of bounds y={newY} minY={MIN_Y} maxY={state.max_y}")

    def _check_claw_for_ongoing_operations(self, state: StateModel, claw_index: int):
        if (state.claws[claw_index].operating_claw):
            raise IllegalBallControlStateError("Claw already opening or closing")
        
        if (state.claws[claw_index].moving_horizontally or state.claws[claw_index].moving_vertically):
            raise IllegalBallControlStateError("Marble dropped while claw is in motion")

    def open_claw(self, state: StateModel, claw_index: int):
        self._check_claw_index(state=state, claw_index=claw_index)

        if not is_ball_in_claw(state, claw_index=claw_index):
            return
        
        self._check_claw_for_ongoing_operations(state=state, claw_index=claw_index)

        if state.claws[claw_index].pos.y != get_top_vacant_index(state, claw_index=claw_index):
            raise IllegalBallControlStateError(
                f"Illegal drop location. Must be topmost vacant position ({get_top_vacant_index(state, claw_index=claw_index)}). Y={state.claws[claw_index].pos.y}."
            )

    def close_claw(self, state: StateModel, claw_index: int):
        self._check_claw_index(state=state, claw_index=claw_index)

        if not is_ball_at_current_pos(state, claw_index=claw_index):
            return
        
        self._check_claw_for_ongoing_operations(state=state, claw_index=claw_index)

        if state.claws[claw_index].pos.y != get_top_occupied_index(state, claw_index=claw_index):
            raise IllegalBallControlStateError(
                f"Illegal grab. Must be topmost marble position ({get_top_occupied_index(state, claw_index=claw_index)}). Y={state.claws[claw_index].pos.y}."
            )
