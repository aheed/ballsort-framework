import asyncio
from dataclasses import replace
import sys

from test_utils import move_ball
sys.path.append("../src/ballsort")

from control_factory import get_control_sim
from ch3_scenario import Ch3Scenario
from state_update_model import StateBall, StatePosition


def goal_state():
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

        def __get_temporary_position(x: int, i: int) -> StatePosition:
            return StatePosition(x=i if i < x else i+1, y=0 if i < 3 else 4)

        for i in range(4):
            src = StatePosition(x=x, y=i+1)
            dst = __get_temporary_position(x=x, i=i)
            await move_ball(bc=bc, src=src, dest=dst)
        for i in range(4):
            src = __get_temporary_position(x=x, i=i)
            dst = StatePosition(x=x, y=4-i)
            await move_ball(bc=bc, src=src, dest=dst)

    for i in range(4):
        await sort_column(x=i)

    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")

def test_ch3():
    goal_state()
    asyncio.run(example_solution())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch3()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.3f} seconds.")
