import asyncio
from dataclasses import replace
import sys
sys.path.append("../content/ballsortutils")

from ball_control import IllegalBallControlStateError
from test_utils import move_ball, move_ball_by_column
from control_factory import get_ch4_control_sim
from ch4_scenario import Ch4Scenario
from state_update_model import StateBall, StatePosition


def test_goal_state():
    sc = Ch4Scenario()
    
    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=2, y=0), color="gray", value=1),
        StateBall(pos=StatePosition(x=2, y=1), color="gray", value=2),
        StateBall(pos=StatePosition(x=2, y=2), color="gray", value=3),
        StateBall(pos=StatePosition(x=2, y=3), color="gray", value=4),
        StateBall(pos=StatePosition(x=2, y=4), color="gray", value=5),
        StateBall(pos=StatePosition(x=2, y=5), color="gray", value=6),
    ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True

async def test_validation():
    bc = get_ch4_control_sim(0)
    await bc.set_scenario(Ch4Scenario())

    await move_ball(bc=bc, src=StatePosition(x=0, y=0), dest=StatePosition(x=1, y=5))

    exception_caught = False
    try:
        # dropping high ball on low ball: illegal move
        await move_ball(bc=bc, src=StatePosition(x=0, y=1), dest=StatePosition(x=1, y=4))
    except IllegalBallControlStateError:
        exception_caught = True

    assert(exception_caught)



async def example_solution():
    bc = get_ch4_control_sim(0)
    await bc.set_scenario(Ch4Scenario())

    async def move_tower(height: int, src_x:int, dest_x:int):
        if height == 1:
            await move_ball_by_column(bc=bc, src_x=src_x, dest_x=dest_x)
            return
        
        intermediate_x = 3 - src_x - dest_x
        await move_tower(height=height - 1, src_x=src_x, dest_x=intermediate_x)
        await move_ball_by_column(bc=bc, src_x=src_x, dest_x=dest_x)
        await move_tower(height=height - 1, src_x=intermediate_x, dest_x=dest_x)

    await move_tower(height=bc.get_state().max_y + 1, src_x=0, dest_x=2)

def main():
    test_goal_state()
    asyncio.run(test_validation())
    asyncio.run(example_solution())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
