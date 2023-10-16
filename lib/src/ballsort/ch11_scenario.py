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
class Ch11Scenario(Scenario):
    """Challenge Implementation"""

    max_x = 8
    max_y = 6
    left_color = "lightblue"
    right_color = "yellow"
    reveal_action = RevealAction(pos=StatePosition(x=max_x // 2, y=max_y))

    def __init__(self, seed: int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"""
Blue marbles sorted by value in the leftmost column. Lowest value on top.
Yellow marbles sorted by value in the rightmost column.
Each marble has an, initially hidden, integer value in the range [1, {(self.max_x//2)-1}].
A marble must be dropped on position ({self.max_x//2}, {self.max_y}) to reveal its value.
Claw 0 can operate in columns 0-{self.max_x//2}. Claw 1 can operate in columns {self.max_x//2}-{self.max_x}.
{self.get_dimensions_description()}"""

    def get_initial_state(self) -> StateModel:
        random.seed(self._seed)

        def get_value_y_pairs():
            return [(random.randint(1, (self.max_x // 2) - 1), y) for y in range(1, 7)]

        blue_balls = [
            StateBall(
                pos=StatePosition(x=0, y=y),
                color=self.left_color,
                value=v,
                label="?",
                value_visible=False,
            )
            for (v, y) in get_value_y_pairs()
        ]
        yellow_balls = [
            StateBall(
                pos=StatePosition(x=self.max_x, y=y),
                color=self.right_color,
                value=v,
                label="?",
                value_visible=False,
            )
            for (v, y) in get_value_y_pairs()
        ]

        highlights = [
            Highlight(
                xMin=self.max_x // 2,
                xMax=self.max_x // 2,
                yMin=self.max_y,
                yMax=self.max_y,
                color="lightyellow",
            )
        ]

        claw0 = replace(get_default_state().claws[0], max_x = self.max_x//2)
        claw1 = replace(claw0, pos=StatePosition(x=6, y=0), min_x=self.max_x//2, max_x = self.max_x)

        return replace(
            get_default_state(),
            balls=blue_balls + yellow_balls,
            max_x=self.max_x,
            max_y=self.max_y,
            highlights=highlights,
            claws=[claw0, claw1]
        )

    def _is_column_in_goal_state(self, state: StateModel, x: int, color: str) -> bool:
        column: list[StateBall] = [
            ball for ball in state.balls if ball.pos.x == x and ball.color == color
        ]

        if len(column) != len(state.balls) // 2:
            return False

        actual_values = [
            0 if ball.value is None else ball.value
            for ball in sorted(column, key=lambda ball: ball.pos.y)
        ]
        expected_values = sorted(actual_values)

        return expected_values == actual_values

    def is_in_goal_state(self, state: StateModel) -> bool:
        # No ball in claw
        if state.claws[0].ball_color:
            return False

        return self._is_column_in_goal_state(
            state=state, x=0, color=self.left_color
        ) and self._is_column_in_goal_state(
            state=state, x=self.max_x, color=self.right_color
        )

    def on_ball_dropped(
        self, state: StateModel, ball: StateBall
    ) -> tuple[StateModel, bool]:
        """Override"""
        return self.reveal_action.on_ball_dropped(state=state, ball=ball)
