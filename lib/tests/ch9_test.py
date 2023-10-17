import asyncio
import sys
sys.path.append("../src/ballsort")

from test_utils import move_ball_by_column, sort_column
from control_factory import get_control_sim
from ch9_scenario import Ch9Scenario


async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch9Scenario(seed=4711))

    # reveal each ball's value by moving it to the revealer spot. Then move it to column 2.
    for _ in range(len(bc.get_state().balls)):
        await move_ball_by_column(bc=bc, src_x=1, dest_x=4) # reveal
        await move_ball_by_column(bc=bc, src_x=4, dest_x=2) # make room for another ball

    await sort_column(bc=bc, src_x1=1, src_x2=2, dest_x=0, nof_balls=len(bc.get_state().balls), claw_index=0)

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def test_ch9():
    asyncio.run(example_solution())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch9()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
