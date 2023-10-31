from dataclasses import dataclass, replace
import random
from ball_control import IllegalBallControlStateError
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch13Scenario(Scenario):
    """Challenge Implementation"""

    max_x = 6
    max_y = 3
    colors = ["lightblue", "pink", "lightgreen", "lightyellow", "gray"]
    nof_colors = 5  # 0-4

    def __init__(self, seed: int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"""
        Each marble color in a single column.
        A marble can not be dropped on top of a marble of different color.
        maxX={self.max_x}, maxY={self.max_y}"""

    def get_initial_state(self) -> StateModel:
        random.seed(self._seed)

        nof_rows = self.max_y + 1
        nof_columns = self.max_x + 1        

        def __create_random_ball_list():
            nof_empty_columns = nof_columns - self.nof_colors

            color_bag = [
                color for color in range(self.nof_colors) for _ in range(self.max_y + 1)
            ]
            return random.sample(color_bag, len(color_bag)) + [
                self.nof_colors for _ in range(nof_empty_columns * nof_rows)
            ]

        def __get_ball_index(x: int, y: int) -> int:
            assert(x >= 0)
            assert(x <= self.max_x)
            assert(y >= 0)
            assert(y <= self.max_y)
            return x * nof_rows + y

        coordinates = __create_random_ball_list()

        def __get_state_position_by_ball_index(ball_index: int) -> StatePosition:
            x = ball_index // nof_rows
            y = ball_index % nof_rows
            assert __get_ball_index(x=x, y=y) == ball_index
            return StatePosition(x=x, y=y)

        balls = [
            StateBall(
                pos=__get_state_position_by_ball_index(ball_index),
                color=self.colors[coordinates[ball_index]],
            )
            for ball_index in range(len(coordinates))
            if coordinates[ball_index] != self.nof_colors
        ]

        return replace(
            get_default_state(), balls=balls, max_x=self.max_x, max_y=self.max_y
        )

    def is_in_goal_state(self, state: StateModel) -> bool:
        # No ball in claw
        if state.claws[0].ball:
            return False

        columns: list[list[StateBall]] = [[] for _ in range(state.max_x + 1)]
        for ball in state.balls:
            columns[ball.pos.x].append(ball)

        # No more than one color per column
        return next((False for column in columns if (len(column) != (self.max_y+1) and len(column) != 0) or len(set([ball.color for ball in column])) > 1), True)

    def on_ball_dropped(
        self, state: StateModel, ball: StateBall
    ) -> tuple[StateModel, bool]:
        """Override"""
        ball_below_dropped = next((bball for bball in state.balls if bball.pos == StatePosition(x=ball.pos.x, y=ball.pos.y+1)), None)
        if ball_below_dropped is None:
            return (state, False)
        
        if ball_below_dropped.color != ball.color:
            raise IllegalBallControlStateError(f"Ball ({ball.color}) dropped on top of ball of different color ({ball_below_dropped.color})")

        return (state, False)
    