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

    max_x = 7
    max_y = 3
    colors = ["lightblue", "pink", "lightgreen", "lightyellow", "gray"]
    nof_colors = 5  # 0-4

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

        def __create_random_ball_list(nof_empty_columns: int):
            color_bag = [
                color for color in range(self.nof_colors) for _ in range(self.max_y + 1)
            ]
            return random.sample(color_bag, len(color_bag)) + [
                self.nof_colors for _ in range(nof_empty_columns * rows)
            ]

        # ball_list = __create_random_ball_list(nof_empty_columns=2)

        def __get_ball_index(x: int, y: int) -> int:
            return x * rows + y

        def __get_color(balls: list[int], x: int, y: int) -> int:
            return balls[__get_ball_index(x=x, y=y)]

        def __get_columns(balls: list[int]) -> list[list[int]]:
            return [
                balls[n * (self.max_y + 1) : (n + 1) * (self.max_y + 1)]
                for n in range(self.nof_colors)
            ]

        def __is_in_goal_state(balls: list[int]) -> bool:
            columns = __get_columns(balls=balls)
            return next((False for column in columns if len(set(column)) != 1), True)

        # def __get_top_by_column(column: list[str]) -> tuple[str, int]:
        #    src_y = -1
        #    src_color = empty_color
        #    for y in range(self.max_y + 1):
        #        if column[y] != empty_color:
        #            src_y = y
        #            src_color = column[y]
        #            break
        #    return (src_color, src_y)

        def __get_top_index(balls: list[int], x: int) -> int:
            src_y = self.max_y + 1
            for y in range(self.max_y + 1):
                if __get_color(balls=balls, x=x, y=y) != self.nof_colors:
                    src_y = y
                    break
            return src_y

            # return next((color for color in column if color != empty_color), empty_color)

        def __is_move_legal(balls: list[int], move: tuple[int, int]) -> bool:
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

        def __get_legal_moves(balls: list[int]) -> list[tuple[int, int]]:
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

        def __get_zobrist_index_old(x: int, y: int, color: int) -> int:
            return (
                color * (self.max_x + 1) * (self.max_y + 1) + y * (self.max_x + 1) + x
            )

        def __get_zobrist_index(ball_index: int, color: int) -> int:
            return ball_index * (self.nof_colors) + color

        zobrist_dict: dict[int, int] = {}
        for x in range(self.max_x + 1):
            for y in range(self.max_y + 1):
                for color in range(self.nof_colors):
                    zobrist_dict[
                        __get_zobrist_index(
                            ball_index=__get_ball_index(x=x, y=y), color=color
                        )
                    ] = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        # for x in range(self.max_x+1):
        #    for y in range(self.max_y+1):
        #        for color in range(self.nof_colors):
        #            zobrist_dict[__get_zobrist_index(x=x, y=y, color=color)] = random.randint(0, 0xFFFFFFFFFFFFFFFF)

        def __calc_hash(balls: list[int]) -> int:
            hash = 0
            for x in range(self.max_x + 1):
                for y in range(self.max_y + 1):
                    ball_index = __get_ball_index(x=x, y=y)
                    hash = (
                        hash
                        ^ zobrist_dict[
                            __get_zobrist_index(
                                ball_index=ball_index, color=balls[ball_index]
                            )
                        ]
                    )
            return hash

        def __is_winnable(
            balls: list[int], previous_positions: set[int], position_hash: int
        ) -> bool:
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
                post_move_state[src_index] = self.nof_colors

                # new_position_hash = __calc_hash_incrementally(start_hash=position_hash, move=move)
                new_position_hash = __calc_hash(balls=post_move_state)

                if position_hash not in previous_positions:
                    all_positions = previous_positions.union({new_position_hash})

                    if __is_winnable(
                        balls=post_move_state,
                        previous_positions=all_positions,
                        position_hash=new_position_hash,
                    ):
                        return True
                else:
                    print("Position has been evaluated before. Skip.")

            return False

        def __is_starting_position_winnable(balls: list[int]) -> bool:
            hash = __calc_hash(balls=balls)
            return __is_winnable(
                balls=balls, previous_positions=set(), position_hash=hash
            )

        coordinates = __create_random_ball_list(nof_empty_columns=2)
        while not __is_starting_position_winnable(balls=coordinates):
            print("unwinnable starting position. Trying again.")
            coordinates = __create_random_ball_list(nof_empty_columns=2)

        def __get_state_position_by_ball_index(ball_index: int) -> StatePosition:
            x = ball_index // rows
            y = ball_index % rows
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
        return next((False for column in columns if len(set([ball.color for ball in column])) > 1), True)

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
    