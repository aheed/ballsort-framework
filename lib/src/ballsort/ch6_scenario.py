from dataclasses import dataclass, replace
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch6Scenario(Scenario):
    """Challenge Implementation"""

    def get_goal_state_description(self) -> str:
        return f"Swap positions\n{self.get_dimensions_description()}"
    
    def get_initial_state(self) -> StateModel:
        max_x = 4
        max_y = 4
        balls = [
            StateBall(pos=StatePosition(x=0, y=4), color="yellow"),
            StateBall(pos=StatePosition(x=4, y=4), color="blue"),
        ]

        claw0 = get_default_state().claws[0]
        claw1 = replace(claw0, pos = StatePosition(x=4, y=0))
        claws = [claw0, claw1]
        
        return replace(get_default_state(), balls = balls, max_x=max_x, max_y=max_y, claws=claws)

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in claw
        if state.claws[0].ball_color:
            return False
        
        column0: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 0]
        column4: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 4]

        if len(column0) != 1 or column0[0].color != "blue":
            return False
        
        if len(column4) != 1 or column4[0].color != "yellow":
            return False
        
        return True
    