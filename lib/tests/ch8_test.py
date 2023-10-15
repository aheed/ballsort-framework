import asyncio
from dataclasses import replace
import sys
sys.path.append("../src/ballsort")

from test_utils import sort_column
from control_factory import get_control_sim
from ch8_scenario import Ch8Scenario
from state_update_model import StateBall, StatePosition
from ball_control import IllegalBallControlStateError

def test_goal_state():
    sc = Ch8Scenario()

    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=0, y=2), color="lightblue", value=101),
        StateBall(pos=StatePosition(x=0, y=3), color="lightblue", value=102),
        StateBall(pos=StatePosition(x=0, y=4), color="lightblue", value=103),
        StateBall(pos=StatePosition(x=0, y=5), color="lightblue", value=104),
        StateBall(pos=StatePosition(x=0, y=6), color="lightblue", value=105),

        StateBall(pos=StatePosition(x=6, y=2), color="yellow", value=101),
        StateBall(pos=StatePosition(x=6, y=3), color="yellow", value=102),
        StateBall(pos=StatePosition(x=6, y=4), color="yellow", value=103),
        StateBall(pos=StatePosition(x=6, y=5), color="yellow", value=104),
        StateBall(pos=StatePosition(x=6, y=6), color="yellow", value=105),
    ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True

async def test_claw_0_position_limit():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch8Scenario())    
    exception_caught = False

    try:
        # moving claw to x coordinate > 2: Illegal
        await bc.move_horizontally(3, claw_index=0)
    except IllegalBallControlStateError as caught_err:
        exception_caught = True
        print(f"Expected exception caught: {caught_err}")

    assert(exception_caught)

async def test_claw_1_position_limit():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch8Scenario())
    exception_caught = False

    try:
        # moving claw to x coordinate < 4: Illegal
        await bc.move_horizontally(-3, claw_index=1)
    except IllegalBallControlStateError as caught_err:
        exception_caught = True
        print(f"Expected exception caught: {caught_err}")

    assert(exception_caught)
   
async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch8Scenario(seed=45))

    a = sort_column(bc=bc, src_x1=1, src_x2=2, dest_x=0, nof_balls= len(bc.get_state().balls)//2, claw_index=0)
    b = sort_column(bc=bc, src_x1=4, src_x2=5, dest_x=6, nof_balls= len(bc.get_state().balls)//2, claw_index=1)
    await asyncio.gather(a, b)

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def main():
    test_goal_state()
    asyncio.run(test_claw_0_position_limit())
    asyncio.run(test_claw_1_position_limit())
    asyncio.run(example_solution())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
