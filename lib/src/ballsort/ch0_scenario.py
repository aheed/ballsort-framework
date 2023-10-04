from dataclasses import dataclass, replace
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch0Scenario(Scenario):
    """Challenge Implementation"""

    def get_goal_state_description(self) -> str:
        return f"All marbles shall be in the leftmost column.\n{self.get_dimensions_description()}"
    
    def get_initial_state(self) -> StateModel:
        balls = [
            StateBall(pos=StatePosition(x=3, y=4), color="blue"),
            StateBall(pos=StatePosition(x=2, y=4), color="blue"),
            StateBall(pos=StatePosition(x=1, y=4), color="green"),
        ]
        return replace(get_default_state(), balls = balls)

    def is_in_goal_state(self, state: StateModel) -> bool:
        
        columns: list[list[StateBall]] = [[] for _ in range(state.max_x + 1)]
        for ball in state.balls:
            columns[ball.pos.x].append(ball)

        # No ball in claw
        if state.claw.ball_color:
            return False

        # 3 balls in leftmost column
        if len(columns[0]) != 3:
            return False

        return True
    