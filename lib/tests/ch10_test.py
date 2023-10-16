import asyncio
import sys
sys.path.append("../src/ballsort")

from test_utils import move_ball_by_column
from control_factory import get_control_sim
from ch10_scenario import Ch10Scenario
from state_update_model import StatePosition


async def example_solution():
    """Bucket sort solution"""
    
    bc = get_control_sim(0)
    await bc.set_scenario(Ch10Scenario(seed=4711))

    reveal_spot_x = bc.get_state().max_x
    reveal_spot_y = bc.get_state().max_y

    # reveal each ball's value by moving it to the revealer spot. Then move it to bucket column.
    for _ in range(len(bc.get_state().balls)):
        await move_ball_by_column(bc=bc, src_x=0, dest_x=reveal_spot_x) # reveal
        revealed_value = next((ball.value for ball in bc.get_state().balls if ball.pos == StatePosition(x=reveal_spot_x, y=reveal_spot_y)), None)
        assert(revealed_value)
        await move_ball_by_column(bc=bc, src_x=reveal_spot_x, dest_x=revealed_value) # move to column corresponding to value

    # Finally move all buckets to column 0 in the correct order
    for x in range(3, 0, -1):
        nof_balls_in_column = len([ball for ball in bc.get_state().balls if ball.pos.x == x])
        for _ in range(nof_balls_in_column):
            await move_ball_by_column(bc=bc, src_x=x, dest_x=0)

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def main():
    asyncio.run(example_solution())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
