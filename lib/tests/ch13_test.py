import asyncio
import sys

sys.path.append("../src/ballsort")

from test_utils import get_column_top_occupied_pos, get_column_top_vacant_pos, go_to_pos, move_ball_by_column
from control_factory import get_control_sim
from ch13_scenario import Ch13Scenario
from state_update_model import StatePosition
from ball_control import BallControl




async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch13Scenario(seed=6588)) #6589

    # todo: implement solution
    
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
