import asyncio
from dataclasses import replace
import sys
sys.path.append("../src/ballsort")

from test_utils import sort_column
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
    await bc.set_scenario(Ch7Scenario(seed=4711))

    await sort_column(bc=bc, src_x1=1, src_x2=2, dest_x=0, nof_balls=len(bc.get_state().balls), claw_index=0)

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
