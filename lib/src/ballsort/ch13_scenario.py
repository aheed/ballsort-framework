from dataclasses import dataclass, replace
import random
from reveal_color_value_action import RevealColorValueAction
from scenario import Scenario
from state_update_model import (
    Highlight,
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch13Scenario(Scenario):
    """Challenge Implementation"""

    max_x = 7
    max_y = 3
    colors = ["lightblue", "pink", "lightgreen", "lightyellow", "gray"]

    def __init__(self, seed: int | None = None):
        super().__init__(seed=seed)

    def get_goal_state_description(self) -> str:
        return f"""
        Only marbles of a single color in any column. 
        A marble can not be dropped on top of a marble of different color.
        {self.get_dimensions_description()}"""

    def get_initial_state(self) -> StateModel:
        random.seed(self._seed)

        rows = self.max_y + 1
        empty_color = "nothing"

        def __create_random_ball_list(nof_empty_columns: int):
            color_bag = [color for color in self.colors for _ in range(self.max_y + 1)]
            return random.sample(color_bag, len(color_bag)) + [
                empty_color for _ in range(nof_empty_columns * rows)
            ]

        # ball_list = __create_random_ball_list(nof_empty_columns=2)

        def __get_ball_index(x: int, y: int) -> int:
            return y * rows + x

        def __get_color(balls: list[str], x: int, y: int) -> str:
            return balls[__get_ball_index(x=x, y=y)]

        def __get_columns(balls: list[str]) -> list[list[str]]:
            return [
                balls[n * (self.max_y + 1) : (n + 1) * (self.max_y + 1)]
                for n in range(len(self.colors))
            ]

        def __is_in_goal_state(balls: list[str]) -> bool:
            columns = __get_columns(balls=balls)
            return next((False for column in columns if len(set(column)) != 1), True)

        def __get_top_by_column(column: list[str]) -> tuple[str, int]:
            src_y = -1
            src_color = empty_color
            for y in range(self.max_y + 1):
                if column[y] != empty_color:
                    src_y = y
                    src_color = column[y]
                    break
            return (src_color, src_y)

        def __get_top_index(balls: list[str], x: int) -> int:
            src_y = self.max_y + 1
            for y in range(self.max_y + 1):
                if __get_color(balls=balls, x=x, y=y) != empty_color:
                    src_y = y
                    break
            return src_y

            # return next((color for color in column if color != empty_color), empty_color)

        def __is_move_legal(balls: list[str], move: tuple[int, int]) -> bool:
            src_x, dest_x = move
            src_y = __get_top_index(balls=balls, x=src_x)
            if src_y < 0:
                return False  # source column is empty. Not legal.

            dest_col_top_y = __get_top_index(balls=balls, x=dest_x)
            if dest_col_top_y > self.max_y:
                return True  # destination column is empty. Legal.

            if dest_col_top_y == 0:
                return False  # destination column is full. Not Legal.

            return __get_color(balls=balls, x=src_x, y=src_y) == __get_color(
                balls=balls, x=dest_x, y=dest_col_top_y
            )

        def __get_legal_moves(balls: list[str]) -> list[tuple[int, int]]:
            all_moves = [
                (src_col, dest_col)
                for src_col in range(self.max_x)
                for dest_col in range(self.max_x)
                if src_col != dest_col
            ]
            legal_moves = [
                move for move in all_moves if __is_move_legal(balls=balls, move=move)
            ]
            return legal_moves
        
        def __get_zobrist_index(x: int, y:int, color: str)

        def __is_winnable(balls: list[str], previous_positions: set[int], position_hash: int) -> bool:
            if __is_in_goal_state(balls=balls):
                return True

            # try candidates
            for move in __get_legal_moves(balls=balls):
                src_x, dest_x = move
                src_y = __get_top_index(balls=balls, x=src_x)
                dest_y = min(__get_top_index(balls=balls, x=dest_x), self.max_y)
                src_index = __get_ball_index(x=src_x, y=src_y)
                dest_index = __get_ball_index(x=dest_x, y=dest_y)
                post_move_state = balls.copy()
                post_move_state[dest_index] = balls[src_index]
                post_move_state[src_index] = empty_color

                #new_position_hash = __calc_hash_incrementally(start_hash=position_hash, move=move)
                new_position_hash = __calc_hash(balls=balls)

                all_positions = previous_positions.union({new_position_hash})

                if __is_winnable(
                    balls=post_move_state,
                    previous_positions=all_positions,
                    position_hash=new_position_hash
                ):
                    return True

            return False

        def __is_starting_position_winnable(balls: list[str]) -> bool:
            hash = __calc_hash(balls=balls)
            return __is_winnable(balls=balls, previous_positions=set(), position_hash=)

        ball_colors = __create_random_ball_list(nof_empty_columns=2)
        while not __is_starting_position_winnable(balls=ball_colors):
            print("unwinnable starting position. Trying again.")
            ball_colors = __create_random_ball_list(nof_empty_columns=2)

        ###

        nof_balls = 2 * self.nof_colors
        values = random.sample(range(1, self.nof_colors + 1), self.nof_colors)
        min_y = self.max_y + 1 - nof_balls
        left_y = random.sample(range(min_y, self.max_y + 1), nof_balls)

        ball_colors = [
            StateBall(
                pos=StatePosition(x=0, y=left_y[i]),
                color=self.colors[i % self.nof_colors],
                value=values[i % self.nof_colors],
                label="?",
                value_visible=False,
            )
            for i in range(nof_balls)
        ]

        return replace(
            get_default_state(), balls=ball_colors, max_x=self.max_x, max_y=self.max_y
        )

    def is_in_goal_state(self, state: StateModel) -> bool:
        # No ball in claw
        if state.claws[0].ball:
            return False

        return next(
            (
                False
                for ball in state.balls
                if ball.pos.x < 4 and ball.pos.x != ball.value
            ),
            True,
        )

    def on_ball_dropped(
        self, state: StateModel, ball: StateBall
    ) -> tuple[StateModel, bool]:
        """Override"""
        return self.reveal_action.on_ball_dropped(state=state, ball=ball)
