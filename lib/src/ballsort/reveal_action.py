from dataclasses import dataclass, replace
from state_update_model import StateBall, StateModel, StatePosition

@dataclass
class RevealAction:
    """Reveal a ball's value when it's dropped in a specific location."""

    pos: StatePosition

    def on_ball_dropped(self, state: StateModel, ball: StateBall) -> tuple[StateModel, bool]:
        if ball.pos != self.pos:
            return state, False

        ball_positions = [ball.pos for ball in state.balls]
        ball_index = ball_positions.index(self.pos)

        state.balls[ball_index].value_visible = True
        if state.balls[ball_index].label == "?":
            state.balls[ball_index].label = f"{state.balls[ball_index].value}"

        return replace(state, balls=state.balls), True
