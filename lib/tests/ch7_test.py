import asyncio
from dataclasses import replace
import sys
sys.path.append("../src/ballsort")

from test_utils import move_ball_by_column
from control_factory import get_control_sim
from ch7_scenario import Ch7Scenario
from state_update_model import StateBall, StatePosition

def test_goal_state():
    sc = Ch7Scenario()

    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
            StateBall(pos=StatePosition(x=0, y=3), color="yellow", value=3, label=f"{3}"),
            StateBall(pos=StatePosition(x=0, y=6), color="yellow", value=12, label=f"{12}"),
            StateBall(pos=StatePosition(x=0, y=2), color="yellow", value=-4, label=f"{-4}"),
            StateBall(pos=StatePosition(x=0, y=5), color="yellow", value=7, label=f"{7}"),
            StateBall(pos=StatePosition(x=0, y=4), color="yellow", value=3, label=f"{3}"),
        ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state)


async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch7Scenario())

    for _ in range(len(bc.get_state().balls)):

        column1: list[StateBall] = [ball for ball in bc.get_state().balls if ball.pos.x == 1]
        column2: list[StateBall] = [ball for ball in bc.get_state().balls if ball.pos.x == 2]
        column1_sorted = [ball.value for ball in sorted(column1, key=lambda ball: ball.pos.y)]
        column2_sorted = [ball.value for ball in sorted(column2, key=lambda ball: ball.pos.y)]

        if len(column1_sorted) == 0:
            src_column_index = 2
        elif len(column2_sorted) == 0:
            src_column_index = 1
        else:
            src_column_index = 1 if max(column1_sorted) >= max(column2_sorted) else 2

        dest_column_index = 2 if src_column_index == 1 else 1
        src_column = [column1_sorted, column2_sorted][src_column_index - 1]
        
        minpos = src_column.index(max(src_column))

        for _ in range(minpos):
            await move_ball_by_column(bc=bc, src_x=src_column_index, dest_x=dest_column_index)

        await move_ball_by_column(bc=bc, src_x=src_column_index, dest_x=0)

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def main():
    test_goal_state()
    asyncio.run(example_solution())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
