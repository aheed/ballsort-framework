import asyncio
import random
import sys
import pathlib
abspath = pathlib.Path(__file__).parent.joinpath("../src/ballsort").resolve()
sys.path.append(f"{abspath}")

from test_utils import get_column_top_occupied_pos, get_column_top_vacant_pos, go_to_pos, move_ball_by_column
from control_factory import get_control_sim
from ch13_scenario import Ch13Scenario
from state_update_model import StatePosition
from ball_control import BallControl

repeat_positions = 0

async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch13Scenario(seed=6587)) #6589

    nof_rows = bc.get_state().max_y + 1
    nof_columns = bc.get_state().max_x + 1        
    nof_colors = nof_columns - 2 # assume two empty columns

    colors = list(set([ball.color for ball in bc.get_state().balls]))
    empty_color = len(colors)

    def __get_ball_index(x: int, y: int) -> int:
        assert(x >= 0)
        assert(x <= bc.get_state().max_x)
        assert(y >= 0)
        assert(y <= bc.get_state().max_y)
        return x * nof_rows + y
    
    def __get_ball_list() -> list[int]:
        #balls: list[int] = []
        #for x in range(nof_columns):
        #    for y in range(nof_rows):
        #        balls[__get_ball_index(x=x, y=y)] = empty_color

        balls = [empty_color for _ in range(nof_columns) for _ in range(nof_rows)]

        for ball in bc.get_state().balls:
            balls[__get_ball_index(x=ball.pos.x, y=ball.pos.y)] = colors.index(ball.color)
        return balls

    def __get_color(balls: list[int], x: int, y: int) -> int:
        return balls[__get_ball_index(x=x, y=y)]

    def __get_columns(balls: list[int]) -> list[list[int]]:
        return [
            balls[n * (nof_rows) : (n + 1) * (nof_rows)]
            for n in range(nof_colors)
        ]

    def __is_in_goal_state(balls: list[int]) -> bool:
        columns = __get_columns(balls=balls)
        return next((False for column in columns if len(set(column)) != 1), True)

    def __get_top_index(balls: list[int], x: int) -> int:
        ret = nof_rows
        for y in range(nof_rows):
            if __get_color(balls=balls, x=x, y=y) != nof_colors:
                ret = y
                break
        return ret

    def __is_move_legal(balls: list[int], move: tuple[int, int]) -> bool:
        src_x, dest_x = move
        src_y = __get_top_index(balls=balls, x=src_x)
        if src_y > bc.get_state().max_y:
            return False  # source column is empty. Not legal.

        dest_col_top_y = __get_top_index(balls=balls, x=dest_x)
        if dest_col_top_y > bc.get_state().max_y:
            return True  # destination column is empty. Legal.

        if dest_col_top_y == 0:
            return False  # destination column is full. Not Legal.

        return __get_color(balls=balls, x=src_x, y=src_y) == __get_color(
            balls=balls, x=dest_x, y=dest_col_top_y
        )

    def __get_legal_moves(balls: list[int]) -> list[tuple[int, int]]:
        all_moves = [
            (src_col, dest_col)
            for src_col in range(nof_columns)
            for dest_col in range(nof_columns)
            if src_col != dest_col
        ]
        legal_moves = [
            move for move in all_moves if __is_move_legal(balls=balls, move=move)
        ]
        return legal_moves

    def __get_zobrist_index(ball_index: int, color: int) -> int:
        return ball_index * (nof_colors) + color

    zobrist_dict: dict[int, int] = {}
    for x in range(nof_columns):
        for y in range(nof_rows):
            for color in range(nof_colors + 1): # +1 for the no color (no ball) case
                zobrist_dict[
                    __get_zobrist_index(
                        ball_index=__get_ball_index(x=x, y=y), color=color
                    )
                ] = random.randint(0, 0xFFFFFFFFFFFFFFFF)

    def __calc_hash(balls: list[int]) -> int:
        hash = 0
        for x in range(nof_columns):
            for y in range(nof_rows):
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
    
    def __make_move(balls: list[int], src_x: int, dest_x: int) -> list[int]:
        src_y = __get_top_index(balls=balls, x=src_x)
        dest_y = __get_top_index(balls=balls, x=dest_x) - 1
        src_index = __get_ball_index(x=src_x, y=src_y)
        dest_index = __get_ball_index(x=dest_x, y=dest_y)
        post_move_state = balls.copy()
        post_move_state[dest_index] = balls[src_index]
        post_move_state[src_index] = nof_colors
        return post_move_state

    def __is_winnable(
        balls: list[int], previous_positions: set[int], previous_moves: list[tuple[int, int]], position_hash: int
    ) -> tuple[bool, list[tuple[int, int]]]:
        
        global repeat_positions

        if __is_in_goal_state(balls=balls):
            print(balls)
            return (True, previous_moves)

        # try candidates
        for move in __get_legal_moves(balls=balls):
            src_x, dest_x = move

            post_move_state = __make_move(balls=balls, src_x=src_x, dest_x=dest_x)

            # new_position_hash = __calc_hash_incrementally(start_hash=position_hash, move=move)
            new_position_hash = __calc_hash(balls=post_move_state)

            if new_position_hash not in previous_positions:
                all_positions = previous_positions.union({new_position_hash})

                (winnable, winning_sequence) = __is_winnable(
                    balls=post_move_state,
                    previous_positions=all_positions,
                    previous_moves=previous_moves + [move],
                    position_hash=new_position_hash,
                )
                
                if winnable:
                    return (True, winning_sequence)
            else:
                #print("Position has been evaluated before. Skip.")
                repeat_positions = repeat_positions + 1

        return (False, [])

    def __is_starting_position_winnable(balls: list[int]) -> tuple[bool, list[tuple[int, int]]]:
        hash = __calc_hash(balls=balls)
        return __is_winnable(
            balls=balls, previous_positions=set(), previous_moves=[], position_hash=hash
        )

    color_grid = __get_ball_list()
    print(color_grid, len(color_grid))

    (winning_found, winning_sequence) = __is_starting_position_winnable(balls=color_grid)

    if not winning_found:
        raise ValueError("Unwinnable starting position. should not happen!")

    print(f"winnable position found.\nTotal repeat positions: {repeat_positions}\nwinning sequence in {len(winning_sequence)} moves:{winning_sequence}")

           
    #assert bc.get_state().goal_accomplished

    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def test_ch13():
    asyncio.run(example_solution())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch13()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
