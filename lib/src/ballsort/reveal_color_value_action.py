from dataclasses import dataclass, replace
from state_update_model import StateBall, StateModel, StatePosition

@dataclass
class RevealColorValueAction:
    """Reveal the values of all balls with the same color when a ball is dropped in a specific location."""

    pos: StatePosition

    def on_ball_dropped(self, state: StateModel, ball: StateBall) -> tuple[StateModel, bool]:
        if ball.pos != self.pos:
            return state, False
        
        balls = [replace(b, value_visible = True if b.color==ball.color else b.value_visible) for b in state.balls]
        balls = [replace(b, label = f"{b.value}" if b.value_visible else b.label) for b in balls]

        return replace(state, balls=balls), True
