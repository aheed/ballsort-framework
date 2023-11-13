import asyncio
from dataclasses import replace
import sys
sys.path.append("../src/ballsort")

from test_utils import move_ball_by_column
from control_factory import get_control_sim
from ch6_scenario import Ch6Scenario
from state_update_model import StateBall, StatePosition
from ball_control import IllegalBallControlStateError

def goal_state():
    sc = Ch6Scenario()

    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=0, y=4), color="blue", value=1),
        StateBall(pos=StatePosition(x=4, y=4), color="yellow", value=2),
    ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True

async def claw_collision_validation():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch6Scenario())    
    exception_caught = False

    try:
        # moving claws to overlapping x coordinates: illegal
        await bc.move_horizontally(4, claw_index=0)
    except IllegalBallControlStateError as caught_err:
        exception_caught = True
        print(f"Expected exception caught: {caught_err}")

    assert(exception_caught)

    exception_caught = False
    try:
        # moving claws to overlapping x coordinates: illegal
        await bc.move_horizontally(2, claw_index=0)
        await bc.move_horizontally(-3, claw_index=1)
    except IllegalBallControlStateError as caught_err:
        exception_caught = True
        print(f"Expected exception caught: {caught_err}")

    assert(exception_caught)

async def claw_0_position_limit():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch6Scenario())    
    exception_caught = False

    try:
        # moving claw to x coordinate > 2: Illegal
        await bc.move_horizontally(3, claw_index=0)
    except IllegalBallControlStateError as caught_err:
        exception_caught = True
        print(f"Expected exception caught: {caught_err}")

    assert(exception_caught)

async def claw_1_position_limit():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch6Scenario())    
    exception_caught = False

    try:
        # moving claw to x coordinate < 2: Illegal
        await bc.move_horizontally(-3, claw_index=1)
    except IllegalBallControlStateError as caught_err:
        exception_caught = True
        print(f"Expected exception caught: {caught_err}")

    assert(exception_caught)


async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch6Scenario())

    await move_ball_by_column(bc=bc, src_x=0, dest_x=2, claw_index=0)
    await move_ball_by_column(bc=bc, src_x=4, dest_x=3, claw_index=1)

    await bc.move_horizontally(-1, claw_index=0)
    await move_ball_by_column(bc=bc, src_x=2, dest_x=4, claw_index=1)

    await move_ball_by_column(bc=bc, src_x=3, dest_x=2, claw_index=1)

    await bc.move_horizontally(1, claw_index=1)
    await move_ball_by_column(bc=bc, src_x=2, dest_x=0, claw_index=0)

    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


async def example_solution_concurrent():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch6Scenario())

    await asyncio.gather(
        move_ball_by_column(bc=bc, src_x=0, dest_x=2, claw_index=0),
        move_ball_by_column(bc=bc, src_x=4, dest_x=3, claw_index=1),
    )

    await asyncio.gather(
        bc.move_horizontally(-1, claw_index=0),
        move_ball_by_column(bc=bc, src_x=2, dest_x=4, claw_index=1),
    )

    await move_ball_by_column(bc=bc, src_x=3, dest_x=2, claw_index=1)

    await asyncio.gather(
        bc.move_horizontally(1, claw_index=1),
        move_ball_by_column(bc=bc, src_x=2, dest_x=0, claw_index=0)
    ) 

    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def test_ch6():
    goal_state()
    asyncio.run(claw_collision_validation())
    asyncio.run(claw_0_position_limit())
    asyncio.run(claw_1_position_limit())
    asyncio.run(example_solution())
    asyncio.run(example_solution_concurrent())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch6()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
