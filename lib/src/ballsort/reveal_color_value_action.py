from dataclasses import dataclass, replace
from state_update_model import StateBall, StateModel, StatePosition

@dataclass
class RevealColorValueAction:
    """Reveal the values of all balls with the same color when a ball is dropped in a specific location."""

    pos: StatePosition

    def __reveal_ball(self, src_ball: StateBall, target_ball: StateBall | None) -> StateBall | None:
        if target_ball is None:
            return None
        intermediate_ball = replace(target_ball, value_visible = True if target_ball.color==src_ball.color else target_ball.value_visible)
        ret = replace(intermediate_ball, label = f"{intermediate_ball.value}" if intermediate_ball.value_visible else intermediate_ball.label)
        return ret

    def on_ball_dropped(self, state: StateModel, ball: StateBall) -> tuple[StateModel, bool]:
        if ball.pos != self.pos:
            return state, False
        
        balls = [self.__reveal_ball(src_ball=ball, target_ball=b) for b in state.balls]
        claws = [replace(claw, ball=self.__reveal_ball(src_ball=ball, target_ball=claw.ball)) for claw in state.claws]

        return replace(state, balls=balls, claws=claws), True
