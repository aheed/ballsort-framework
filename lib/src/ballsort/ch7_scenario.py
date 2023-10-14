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

    def get_goal_state_description(self) -> str:
        return f"All marbles sorted by value in the leftmost column. Lowest value on top."
    
    def get_initial_state(self, seed: int | None = None) -> StateModel:
        max_x = 4
        max_y = 6
        random.seed(seed)
        minVal = 0
        maxVal = 10
        ballColor = "yellow"
        balls = [
            StateBall(pos=StatePosition(x=1, y=6), color=ballColor, value=random.randint(minVal, maxVal)),
            StateBall(pos=StatePosition(x=1, y=5), color=ballColor, value=random.randint(minVal, maxVal)),
            StateBall(pos=StatePosition(x=1, y=4), color=ballColor, value=random.randint(minVal, maxVal)),
            StateBall(pos=StatePosition(x=1, y=3), color=ballColor, value=random.randint(minVal, maxVal)),
            StateBall(pos=StatePosition(x=1, y=2), color=ballColor, value=random.randint(minVal, maxVal)),
        ]
        balls = [replace(ball, label=f"{ball.value}") for ball in balls]

        return replace(get_default_state(), balls = balls, max_x=max_x, max_y=max_y)

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in claw
        if state.claws[0].ball_color:
            return False
        
        column0: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 0]

        if len(column0) != len(state.balls):
            return False
        
        actual_values = [ball.value for ball in sorted(state.balls, key=lambda ball: ball.pos.y)]
        expected_values = sorted(actual_values)

        print(expected_values, actual_values)

        return expected_values == actual_values
    