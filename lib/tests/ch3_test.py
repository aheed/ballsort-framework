import asyncio
from dataclasses import replace
import sys

from test_utils import move_ball
sys.path.append("../content/ballsortutils")

from control_factory import get_control_sim
from ch3_scenario import Ch3Scenario
from state_update_model import StateBall, StatePosition


def test_goal_state():
    sc = Ch3Scenario()
    
    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=0, y=1), color="red"),
        StateBall(pos=StatePosition(x=0, y=2), color="red"),
        StateBall(pos=StatePosition(x=0, y=3), color="white"),
        StateBall(pos=StatePosition(x=0, y=4), color="white"),

        StateBall(pos=StatePosition(x=1, y=1), color="red"),
        StateBall(pos=StatePosition(x=1, y=2), color="red"),
        StateBall(pos=StatePosition(x=1, y=3), color="white"),
        StateBall(pos=StatePosition(x=1, y=4), color="white"),

        StateBall(pos=StatePosition(x=2, y=1), color="red"),
        StateBall(pos=StatePosition(x=2, y=2), color="red"),
        StateBall(pos=StatePosition(x=2, y=3), color="white"),
        StateBall(pos=StatePosition(x=2, y=4), color="white"),

        StateBall(pos=StatePosition(x=3, y=1), color="red"),
        StateBall(pos=StatePosition(x=3, y=2), color="red"),
        StateBall(pos=StatePosition(x=3, y=3), color="white"),
        StateBall(pos=StatePosition(x=3, y=4), color="white"),
    ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True


async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch3Scenario())

    async def sort_column(x: int):
        for i in range(4):
            src = StatePosition(x=x, y=i+1)
            dst = StatePosition(x=i if i < x else i+1, y=0 if i < 3 else 4)
            await move_ball(bc=bc, src=src, dest=dst)
        for i in range(4):
            src = StatePosition(x=i if i < x else i+1, y=0 if i < 3 else 4)
            dst = StatePosition(x=x, y=4-i)
            await move_ball(bc=bc, src=src, dest=dst)

    for i in range(4):
        await sort_column(x=i)

def main():
    test_goal_state()
    asyncio.run(example_solution())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
