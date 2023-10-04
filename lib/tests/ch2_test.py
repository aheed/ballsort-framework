import asyncio
from dataclasses import replace
import sys
sys.path.append("../src/ballsort")

from control_factory import get_ch2_control_sim
from ch2_scenario import Ch2Scenario
from state_update_model import StateBall, StatePosition, get_default_state
from test_utils import move_ball


def test_goal_state():
    sc = Ch2Scenario()
    state = get_default_state()
    assert sc.is_in_goal_state(state) == False
    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=0, y=2), color="green"),
        StateBall(pos=StatePosition(x=0, y=3), color="yellow"),
        StateBall(pos=StatePosition(x=0, y=4), color="blue"),
    ]
    state = replace(get_default_state(), balls=balls)
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=0, y=2), color="blue"),
        StateBall(pos=StatePosition(x=0, y=3), color="green"),
        StateBall(pos=StatePosition(x=0, y=4), color="yellow"),
    ]
    state = replace(get_default_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True

async def example_solution_no_scales():
    bc = get_ch2_control_sim(delay_multiplier=0.0)
    async with bc:
        await bc.set_scenario(Ch2Scenario())

        # yellow marble
        await move_ball(bc=bc, src=StatePosition(x=1, y=2), dest=StatePosition(x=0, y=4))

        # green marble
        await move_ball(bc=bc, src=StatePosition(x=1, y=3), dest=StatePosition(x=0, y=3))

        # blue marble
        await move_ball(bc=bc, src=StatePosition(x=1, y=4), dest=StatePosition(x=0, y=2))

def scale_output_positions(scale_output: int) -> tuple[int, int]:
    if scale_output < 0:
        return 2,3
    return 3,2

async def example_solution():
    bc = get_ch2_control_sim(delay_multiplier=0.0)
    sc = Ch2Scenario()
    await bc.set_scenario(sc)

    # populate scale
    await move_ball(bc=bc, src=StatePosition(x=1, y=2), dest=StatePosition(x=2, y=4))
    await move_ball(bc=bc, src=StatePosition(x=1, y=3), dest=StatePosition(x=3, y=4))
    x1_heavy, x1_light = scale_output_positions(await bc.read_scales())

    # move heaviest to leftmost column bottom
    await move_ball(bc=bc, src=StatePosition(x=x1_heavy, y=4), dest=StatePosition(x=0, y=4))

    # move the last one to vacant scale column
    await move_ball(bc=bc, src=StatePosition(x=1, y=4), dest=StatePosition(x=x1_heavy, y=4))

    x2_heavy, x2_light = scale_output_positions(await bc.read_scales())
    
    if x2_heavy == x1_light:
        await move_ball(bc=bc, src=StatePosition(x=x2_heavy, y=4), dest=StatePosition(x=0, y=3))
        await move_ball(bc=bc, src=StatePosition(x=x2_light, y=4), dest=StatePosition(x=0, y=2))
        return

    assert(x1_heavy == x2_heavy)
    assert(x1_light == x2_light)

    # temporarily move the light one to column 1
    await move_ball(bc=bc, src=StatePosition(x=x2_light, y=4), dest=StatePosition(x=1, y=4))

    # col0 -> vacant scale position
    await move_ball(bc=bc, src=StatePosition(x=0, y=4), dest=StatePosition(x=x2_light, y=4))

    x3_heavy, x3_light = scale_output_positions(await bc.read_scales())
    await move_ball(bc=bc, src=StatePosition(x=x3_heavy, y=4), dest=StatePosition(x=0, y=4))
    await move_ball(bc=bc, src=StatePosition(x=x3_light, y=4), dest=StatePosition(x=0, y=3))
    assert(not bc.is_in_goal_state())
    await move_ball(bc=bc, src=StatePosition(x=1, y=4), dest=StatePosition(x=0, y=2))
    assert(bc.is_in_goal_state())
    
def main():
    test_goal_state()
    asyncio.run(example_solution_no_scales())
    asyncio.run(example_solution())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
