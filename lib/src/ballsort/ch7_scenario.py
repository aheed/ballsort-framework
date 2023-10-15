from dataclasses import dataclass, replace
import random
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch7Scenario(Scenario):
    """Challenge Implementation"""

    def __init__(self, seed:int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"All marbles sorted by value in the leftmost column. Lowest value on top."
    
    def get_initial_state(self) -> StateModel:
        max_x = 4
        max_y = 6
        random.seed(self._seed)

        value_y_pairs = [(random.randint(0,10), y) for y in range(2,7)]
        balls = [StateBall(pos=StatePosition(x=1, y=y), color="yellow", value=v, label=f"{v}") for (v,y) in value_y_pairs]

        return replace(get_default_state(), balls = balls, max_x=max_x, max_y=max_y)

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in claw
        if state.claws[0].ball_color:
            return False
        
        column0: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 0]

        if len(column0) != len(state.balls):
            return False
        
        actual_values = [0 if ball.value is None else ball.value for ball in sorted(state.balls, key=lambda ball: ball.pos.y)]
        expected_values = sorted(actual_values)

        #print(expected_values, actual_values)

        return expected_values == actual_values
    