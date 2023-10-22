from dataclasses import dataclass
from ball_control import IllegalBallControlStateError
from state_utils import (
    is_ball_in_claw,
)
from state_update_model import (
    StateModel,
)
from state_validator import StateValidator


@dataclass
class Ch4StateValidator(StateValidator):
    """Validates operations"""

    def open_claw(self, state: StateModel, claw_index: int):
        super().open_claw(state=state, claw_index=claw_index)

        ball_in_claw = state.claws[claw_index].ball
        if not ball_in_claw:
            return

        if state.claws[claw_index].pos.y == state.max_y:
            return

        ball_below = next(
            (
                ball
                for ball in state.balls
                if ball.pos.x == state.claws[claw_index].pos.x and ball.pos.y == state.claws[claw_index].pos.y + 1
            ),
            None,
        )
        if not ball_below:
            return

        # check for values of balls
        if ball_in_claw.value is not None and ball_below.value is not None and ball_below.value < ball_in_claw.value:
            raise IllegalBallControlStateError(
                f"Marble (value={ball_in_claw.value})dropped on top of lower value ({ball_below.value}) marble"
            )
