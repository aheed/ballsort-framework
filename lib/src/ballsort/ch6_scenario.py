from dataclasses import dataclass, replace
from scenario import Scenario
from state_update_model import (
    Highlight,
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch6Scenario(Scenario):
    """Challenge Implementation"""

    def get_goal_state_description(self) -> str:
        return f"Blue in leftmost column. Yellow in rightmost column. Left claw can operate in columns 0-2. Right claw can operate in columns 2-4.\n{self.get_dimensions_description()}"
    
    def get_initial_state(self) -> StateModel:
        max_x = 4
        max_y = 4
        balls = [
            StateBall(pos=StatePosition(x=0, y=4), color="yellow"),
            StateBall(pos=StatePosition(x=4, y=4), color="blue"),
        ]


        claw0 = replace(get_default_state().claws[0], max_x = 2)
        claw1 = replace(claw0, pos=StatePosition(x=4, y=0), min_x=2, max_x = 4)
        claws = [claw0, claw1]

        highlights = [Highlight(xMin=2, xMax=2, yMin=0, yMax=4, color="#eeeeee")]
        
        return replace(get_default_state(), balls = balls, max_x=max_x, max_y=max_y, claws=claws, highlights=highlights)

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in either claw
        if state.claws[0].ball_color:
            return False
        
        if state.claws[1].ball_color:
            return False
        
        column0: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 0]
        column4: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 4]

        if len(column0) != 1 or column0[0].color != "blue":
            return False
        
        if len(column4) != 1 or column4[0].color != "yellow":
            return False
        
        return True
    