import asyncio
import sys

sys.path.append("../src/ballsort")

from test_utils import get_column_top_occupied_pos, get_column_top_vacant_pos, go_to_pos, move_ball_by_column
from control_factory import get_control_sim
from ch11_scenario import Ch11Scenario
from state_update_model import StatePosition
from ball_control_sim import BallControlSim


async def bucket_sort(
    bc: BallControlSim,
    dest_x: int,
    bucket_offset: int,
    claw_index: int,
    lock: asyncio.Lock,
):
    reveal_spot_x = bc.get_state().max_x // 2
    reveal_spot_y = bc.get_state().max_y

    # reveal each ball's value by moving it to the revealer spot. Then move it to bucket column.
    for _ in range(len(bc.get_state().balls) // 2):
        await go_to_pos(bc=bc, dest=get_column_top_occupied_pos(bc=bc, x=dest_x), open_claw=True, claw_index=claw_index)
        await bc.close_claw(claw_index=claw_index)
        async with lock:
            await go_to_pos(bc=bc, dest=StatePosition(x=reveal_spot_x, y=reveal_spot_y), open_claw=False, claw_index=claw_index)
            await bc.open_claw(claw_index=claw_index) # drop should reveal value
            revealed_value = next(
                (
                    ball.value
                    for ball in bc.get_state().balls
                    if ball.pos == StatePosition(x=reveal_spot_x, y=reveal_spot_y)
                ),
                None,
            )
            assert revealed_value
            await bc.close_claw(claw_index=claw_index)
            go_to_bucket_coroutine = go_to_pos(bc=bc, dest=get_column_top_vacant_pos(bc=bc, x=bucket_offset + revealed_value), open_claw=False, claw_index=claw_index)
        await go_to_bucket_coroutine
        await bc.open_claw(claw_index=claw_index)

    # Finally move all buckets to destination column in the correct order
    for x in range(bucket_offset + 3, bucket_offset + 0, -1):
        nof_balls_in_column = len(
            [ball for ball in bc.get_state().balls if ball.pos.x == x]
        )
        for _ in range(nof_balls_in_column):
            await move_ball_by_column(
                bc=bc, src_x=x, dest_x=dest_x, claw_index=claw_index
            )


async def example_solution():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch11Scenario(seed=4711))

    lock = asyncio.Lock() #not really useful in this case

    await bucket_sort(bc=bc, dest_x=0, bucket_offset=0, claw_index=0, lock=lock)
    await bucket_sort(
        bc=bc,
        dest_x=bc.get_state().max_x,
        bucket_offset=bc.get_state().max_x // 2,
        claw_index=1,
        lock=lock,
    )

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


async def example_solution_concurrent():
    bc = get_control_sim(0)
    await bc.set_scenario(Ch11Scenario(seed=4711))

    lock = asyncio.Lock() #necessary to enforce mutually exclusive access to the revealer column

    await asyncio.gather(
        bucket_sort(bc=bc, dest_x=0, bucket_offset=0, claw_index=0, lock=lock),
        bucket_sort(
            bc=bc,
            dest_x=bc.get_state().max_x,
            bucket_offset=bc.get_state().max_x // 2,
            claw_index=1,
            lock=lock,
        ),
    )

    assert bc.get_state().goal_accomplished
    print(f"virtual time elapsed: {bc.get_state().elapsed:0.3f} seconds")


def test_ch11():
    asyncio.run(example_solution())
    asyncio.run(example_solution_concurrent())


if __name__ == "__main__":
    import time

    s = time.perf_counter()
    test_ch11()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")
