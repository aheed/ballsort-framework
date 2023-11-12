import asyncio
from dataclasses import replace
import sys
sys.path.append("../src/ballsort")

from ball_control import BallControl
from test_utils import move_ball_by_column
from control_factory import get_control_sim
from ch14_scenario import Ch14Scenario
from state_update_model import StateBall, StatePosition


def goal_state():
    sc = Ch14Scenario()
    
    state = sc.get_initial_state()
    assert sc.is_in_goal_state(state) == False

    balls = [        
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

        StateBall(pos=StatePosition(x=4, y=1), color="red"),
        StateBall(pos=StatePosition(x=4, y=2), color="red"),
        StateBall(pos=StatePosition(x=4, y=3), color="white"),
        StateBall(pos=StatePosition(x=4, y=4), color="white"),
    ]

    state = replace(sc.get_initial_state(), balls=balls)
    assert sc.is_in_goal_state(state) == True

async def make_moves_single_claw(bc: BallControl,  moves: list[tuple[int, int]]):
    for move in moves:
        src_x, dest_x = move
        await move_ball_by_column(bc=bc, src_x=src_x, dest_x=dest_x)

def get_winning_sequence() -> list[tuple[int, int]]:
    moves: list[tuple[int, int]] = []
    def sort_column(x: int):

        def get_temporary_column(x: int, i: int) -> int:
            return i if i < x else i+1
        
        for i in range(4):
            moves.append((x, get_temporary_column(x=x, i=i)))
        for i in range(4):
            moves.append((get_temporary_column(x=x, i=i), x))

    for i in range(1, 5):
        sort_column(x=i)

    return moves

async def example_solution_single_claw():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch14Scenario())

    await make_moves_single_claw(bc=bc, moves=get_winning_sequence())

    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")

def test_ch14():
    goal_state()
    asyncio.run(example_solution_single_claw())

if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch14()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.3f} seconds.")
