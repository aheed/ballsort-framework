import asyncio
from dataclasses import replace
import sys
sys.path.append("../content/ballsortutils")

from test_utils import move_ball_by_column
from control_factory import get_ch4_control_sim
from ch5_scenario import Ch5Scenario
from state_update_model import StateBall, StatePosition


def test_goal_state():
    sc = Ch5Scenario()
    
    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [
        StateBall(pos=StatePosition(x=2, y=3), color="lightgreen", value=1),
        StateBall(pos=StatePosition(x=2, y=4), color="lightgreen", value=2),
        StateBall(pos=StatePosition(x=2, y=5), color="lightgreen", value=3),
        StateBall(pos=StatePosition(x=3, y=3), color="lightblue", value=1),
        StateBall(pos=StatePosition(x=3, y=4), color="lightblue", value=2),
        StateBall(pos=StatePosition(x=3, y=5), color="lightblue", value=3),
    ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True


async def example_solution():
    bc = get_ch4_control_sim(0)
    await bc.set_scenario(Ch5Scenario())

    await move_ball_by_column(bc=bc, src_x=0, dest_x=3)
    await move_ball_by_column(bc=bc, src_x=0, dest_x=1)
    await move_ball_by_column(bc=bc, src_x=3, dest_x=1)
    await move_ball_by_column(bc=bc, src_x=0, dest_x=3)
    await move_ball_by_column(bc=bc, src_x=0, dest_x=3)

    await move_ball_by_column(bc=bc, src_x=0, dest_x=2)
    await move_ball_by_column(bc=bc, src_x=3, dest_x=2)
    await move_ball_by_column(bc=bc, src_x=3, dest_x=2)
    await move_ball_by_column(bc=bc, src_x=0, dest_x=3)
    await move_ball_by_column(bc=bc, src_x=2, dest_x=0)

    await move_ball_by_column(bc=bc, src_x=2, dest_x=3)
    await move_ball_by_column(bc=bc, src_x=0, dest_x=2)
    await move_ball_by_column(bc=bc, src_x=1, dest_x=2)
    await move_ball_by_column(bc=bc, src_x=1, dest_x=3)
    

def main():
    test_goal_state()
    asyncio.run(example_solution())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
