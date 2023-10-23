import asyncio
import sys

sys.path.append("../src/ballsort")

from test_utils import get_column_top_occupied_pos, get_column_top_vacant_pos, go_to_pos, move_ball_by_column
from control_factory import get_control_sim
from ch12_scenario import Ch12Scenario
from state_update_model import StatePosition
from ball_control import BallControl


async def reveal_color_values(
    bc: BallControl,
    color_to_x: dict[str, int],
    color_to_event: dict[str, asyncio.Event],
    goal_nof_colors: int
):
    """reveal all color values with claw 1"""

    nof_balls = 6  # to reveal
    right_src_x = bc.get_state().max_x - 1
    reveal_x = bc.get_state().max_x
    scrap_x = bc.get_state().max_x - 2

    for _ in range(nof_balls):
        # move to reveal spot (can be done conditionally if the color is already known)
        await move_ball_by_column(
            bc=bc, src_x=right_src_x, dest_x=reveal_x, claw_index=1
        )

        # add revealed color to dict
        revealed_ball = next(
            ball for ball in bc.get_state().balls if ball.pos.x == reveal_x
        )
        assert revealed_ball
        assert revealed_ball.value
        color_to_x[revealed_ball.color] = revealed_ball.value
        ev = color_to_event.get(revealed_ball.color)
        if ev:
            ev.set()
        if len(color_to_x) >= goal_nof_colors:
            break
        # move to scrap heap column
        await move_ball_by_column(bc=bc, src_x=reveal_x, dest_x=scrap_x, claw_index=1)


async def sort_into_buckets(
    bc: BallControl,
    color_to_x: dict[str, int],
    color_to_event: dict[str, asyncio.Event],
):
    """sort into buckets with claw 0"""

    claw_index = 0
    nof_balls = 6  # to sort into buckets
    right_src_x = 0
    max_y = bc.get_state().max_y
    min_y = max_y + 1 - nof_balls
    for y in range(min_y, max_y + 1):
        color = next(
            ball.color
            for ball in bc.get_state().balls
            if ball.pos == StatePosition(x=right_src_x, y=y)
        )
        
        await go_to_pos(bc=bc, dest=get_column_top_occupied_pos(bc=bc, x=right_src_x), open_claw=True, claw_index=claw_index)
        await bc.close_claw(claw_index=claw_index)
        ev = color_to_event.get(color)
        if ev:
            await ev.wait()
        dest_x = color_to_x[color]
        await go_to_pos(bc=bc, dest=get_column_top_vacant_pos(bc=bc, x=dest_x), open_claw=False, claw_index=claw_index)
        await bc.open_claw(claw_index=claw_index)

async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch12Scenario(seed=6589))

    color_to_x: dict[str, int] = {}
    color_to_event: dict[str, asyncio.Event] = {}

    await reveal_color_values(bc=bc, color_to_x=color_to_x, color_to_event=color_to_event, goal_nof_colors=3)
    await sort_into_buckets(bc=bc, color_to_x=color_to_x, color_to_event=color_to_event)

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


async def example_solution_concurrent():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch12Scenario(seed=6589))

    color_to_x: dict[str, int] = {}
    color_to_event: dict[str, asyncio.Event] = {}

    # create an event for each color
    for color in [ball.color for ball in bc.get_state().balls if ball.pos.x == 0]:
        if color_to_event.get(color) == None:
            color_to_event[color] = asyncio.Event()

    # sort and decode concurrently
    await asyncio.gather(
        reveal_color_values(
            bc=bc, color_to_x=color_to_x, color_to_event=color_to_event, goal_nof_colors=3
        ),
        sort_into_buckets(bc=bc, color_to_x=color_to_x, color_to_event=color_to_event),
    )

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def test_ch12():
    asyncio.run(example_solution())
    asyncio.run(example_solution_concurrent())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch12()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
