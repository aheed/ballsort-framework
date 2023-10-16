from dataclasses import dataclass, replace
import random
from reveal_action import RevealAction
from scenario import Scenario
from state_update_model import (
    Highlight,
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch10Scenario(Scenario):
    """Challenge Implementation"""

    reveal_action = RevealAction(pos=StatePosition(x=5, y=6))

    def __init__(self, seed:int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"All marbles sorted by value in the leftmost column. Lowest value on top.\nEach marble has an, initially hidden, integer value in the range [1, 3].\nA marble must be dropped on position (5, 6) to reveal its value."
    
    def get_initial_state(self) -> StateModel:
        max_x = 5
        max_y = 6
        random.seed(self._seed)

        value_y_pairs = [(random.randint(1, 3), y) for y in range(1,7)]
        balls = [StateBall(pos=StatePosition(x=0, y=y), color="cyan", value=v, label="?", value_visible=False) for (v,y) in value_y_pairs]

        highlights = [Highlight(xMin=5, xMax=5, yMin=max_y, yMax=max_y, color="lightyellow")]

        return replace(get_default_state(), balls = balls, max_x=max_x, max_y=max_y, highlights=highlights)

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in claw
        if state.claws[0].ball_color:
            return False
        
        column0: list[StateBall] = [ball for ball in state.balls if ball.pos.x == 0]

        if len(column0) != len(state.balls):
            return False
        
        actual_values = [0 if ball.value is None else ball.value for ball in sorted(state.balls, key=lambda ball: ball.pos.y)]
        expected_values = sorted(actual_values)

        return expected_values == actual_values
    
    def on_ball_dropped(self, state: StateModel, ball: StateBall) -> tuple[StateModel, bool]:
        """Override"""
        return self.reveal_action.on_ball_dropped(state=state, ball=ball)
    