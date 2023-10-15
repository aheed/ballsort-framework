from dataclasses import dataclass, replace
import random
from scenario import Scenario
from state_update_model import (
    Highlight,
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch8Scenario(Scenario):
    """Challenge Implementation"""

    def __init__(self, seed:int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"""
            All blue marbles sorted by value in the leftmost column. Lowest value on top.
            All yellow marbles sorted by value in the rightmost column. Lowest value on top.
            Claw 0 can operate in columns 0-2. Claw 1 can operate in columns 4-6.
            \n{self.get_dimensions_description()}
        """

    def get_initial_state(self) -> StateModel:
        max_x = 6
        max_y = 6
        random.seed(self._seed)
        
        value_y_pairs = [(random.randint(0,10), y) for y in range(2,7)]
        blue_balls = [StateBall(pos=StatePosition(x=2, y=y), color="lightblue", value=v, label=f"{v}") for (v,y) in value_y_pairs]
        value_y_pairs = [(random.randint(0,10), y) for y in range(2,7)]
        yellow_balls = [StateBall(pos=StatePosition(x=4, y=y), color="yellow", value=v, label=f"{v}") for (v,y) in value_y_pairs]

        balls = blue_balls + yellow_balls

        claw0 = replace(get_default_state().claws[0], max_x = 2)
        claw1 = replace(claw0, pos=StatePosition(x=6, y=0), min_x=4, max_x = 6)
        claws = [claw0, claw1]

        highlights = [Highlight(xMin=3, xMax=3, yMin=0, yMax=6, color="gray")]

        return replace(
            get_default_state(),
            balls=balls,
            max_x=max_x,
            max_y=max_y,
            claws=claws,
            highlights=highlights,
        )

    def is_in_goal_state(self, state: StateModel) -> bool:
        # No ball in either claw
        if state.claws[0].ball_color:
            return False
        
        if state.claws[1].ball_color:
            return False

        column0: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 0]
        column6: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 6]

        if len(column0) != len(state.balls) / 2:
            return False
        
        if len(column6) != len(state.balls) / 2:
            return False
        
        actual_col0_values = [0 if ball.value is None else ball.value for ball in sorted(column0, key=lambda ball: ball.pos.y)]
        expected_col0_values = sorted(actual_col0_values)
        if actual_col0_values != expected_col0_values:
            return False
        
        actual_col6_values = [0 if ball.value is None else ball.value for ball in sorted(column6, key=lambda ball: ball.pos.y)]
        expected_col6_values = sorted(actual_col6_values)
        if actual_col6_values != expected_col6_values:
            return False

        return True
