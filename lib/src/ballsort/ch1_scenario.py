from dataclasses import dataclass, replace
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch1Scenario(Scenario):
    """Challenge Implementation"""

    def get_goal_state_description(self) -> str:
        return f"Yellow and pink marbles in separate columns.\n{self.get_dimensions_description()}"
    
    def get_initial_state(self) -> StateModel:
        balls = [
            StateBall(pos=StatePosition(x=0, y=4), color="pink"),
            StateBall(pos=StatePosition(x=0, y=3), color="yellow"),
            StateBall(pos=StatePosition(x=0, y=2), color="pink"),
            StateBall(pos=StatePosition(x=1, y=4), color="yellow"),
        ]
        return replace(get_default_state(), balls = balls)

    def is_in_goal_state(self, state: StateModel) -> bool:
        
        columns: list[list[StateBall]] = [[] for _ in range(state.max_x+1)]
        for ball in state.balls:
            columns[ball.pos.x].append(ball)

        # No ball in claw
        if state.claw.ball_color:
            return False

        # number of non-empty columns shall be 2
        if len([column for column in columns if len(column) != 0]) != 2:
            return False
        
        # number of columns with mixed color balls shall be 0
        if len([column for column in columns if len(set([ball.color for ball in column])) > 1]) != 0:
            return False
        
        return True
    
    