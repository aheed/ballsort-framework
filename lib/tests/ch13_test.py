import asyncio
import sys
import pathlib

abspath = pathlib.Path(__file__).parent.joinpath("../src/ballsort").resolve()
sys.path.append(f"{abspath}")

from color_sorter import ColorSorter
from test_utils import move_ball_by_column
from control_factory import get_control_sim
from ch13_scenario import Ch13Scenario

async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch13Scenario(seed=4050))

    max_x = bc.get_state().max_x
    max_y = bc.get_state().max_y
    color_sorter = ColorSorter(max_x=max_x, max_y=max_y)

    colors = list(set([ball.color for ball in bc.get_state().balls]))
    empty_color = len(colors)

        
    def __get_ball_list() -> list[int]:
        balls = [empty_color for _ in range(color_sorter.nof_columns) for _ in range(color_sorter.nof_rows)]

        for ball in bc.get_state().balls:
            balls[color_sorter.get_ball_index(x=ball.pos.x, y=ball.pos.y)] = colors.index(ball.color)
        return balls

    color_grid = __get_ball_list()
    winning_sequence = color_sorter.find_winning_sequence(balls=color_grid)

    print(f"Positions evaluated:{color_sorter.total_positions}\nrepeated positions:{color_sorter.repeat_positions}\ncache hits:{color_sorter.cache_hits}")
    print(f"Winning sequence in {len(winning_sequence)}  moves:{winning_sequence}")

    for move in winning_sequence:
        src_x, dest_x = move
        await move_ball_by_column(bc=bc, src_x=src_x, dest_x=dest_x)
           
    assert bc.get_state().goal_accomplished

    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def test_ch13():
    asyncio.run(example_solution())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch13()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
