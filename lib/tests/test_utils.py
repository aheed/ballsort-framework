import asyncio
import sys
import pathlib
abspath = pathlib.Path(__file__).parent.joinpath("../src/ballsort").resolve()
sys.path.append(f"{abspath}")

from ball_control import BallControl
from state_update_model import StateBall, StatePosition

async def noop():
    pass

async def go_to_pos(bc: BallControl, dest: StatePosition, open_claw: bool, claw_index: int = 0):
    rel_x = dest.x - bc.get_position(claw_index=claw_index).x
    rel_y = dest.y - bc.get_position(claw_index=claw_index).y
    await asyncio.gather(
        bc.move_horizontally(rel_x, claw_index=claw_index),
        bc.move_vertically(rel_y, claw_index=claw_index),
        bc.open_claw(claw_index=claw_index) if open_claw else noop(),
    )

async def move_ball(
    bc: BallControl, src: StatePosition, dest: StatePosition, claw_index: int = 0
):
    await go_to_pos(bc=bc, dest=src, open_claw=True, claw_index=claw_index)
    await bc.close_claw(claw_index=claw_index)
    await go_to_pos(bc=bc, dest=dest, open_claw=False, claw_index=claw_index)
    await bc.open_claw(claw_index=claw_index)

def get_column_top_occupied_y(bc: BallControl, x: int) -> int:
    return min(
        [ball.pos.y for ball in bc.get_state().balls if ball.pos.x == x],
        default=bc.get_state().max_y,
    )

def get_column_top_occupied_pos(bc: BallControl, x: int) -> StatePosition:
    return StatePosition(x=x, y=get_column_top_occupied_y(bc=bc, x=x))

def get_column_top_vacant_y(bc: BallControl, x: int) -> int:
    return (
        min(
            [ball.pos.y for ball in bc.get_state().balls if ball.pos.x == x],
            default=bc.get_state().max_y + 1,
        )
        - 1
    )

def get_column_top_vacant_pos(bc: BallControl, x: int) -> StatePosition:
    return StatePosition(x=x, y=get_column_top_vacant_y(bc=bc, x=x))

async def move_ball_by_column(
    bc: BallControl, src_x: int, dest_x: int, claw_index: int = 0
):
    await move_ball(
        bc=bc,
        src=get_column_top_occupied_pos(bc=bc, x=src_x),
        dest=get_column_top_vacant_pos(bc=bc, x=dest_x),
        claw_index=claw_index,
    )


async def sort_column(
    bc: BallControl,
    src_x1: int,
    src_x2: int,
    dest_x: int,
    nof_balls: int,
    claw_index: int,
):
    """takes balls from columns src_x1 and src_x2 and puts them, ordered by value, in column dest_x"""

    for _ in range(nof_balls):
        column1: list[StateBall] = [
            ball for ball in bc.get_state().balls if ball.pos.x == src_x1
        ]
        column2: list[StateBall] = [
            ball for ball in bc.get_state().balls if ball.pos.x == src_x2
        ]
        column1_sorted = [
            0 if ball.value is None else ball.value
            for ball in sorted(column1, key=lambda ball: ball.pos.y)
        ]
        column2_sorted = [
            0 if ball.value is None else ball.value
            for ball in sorted(column2, key=lambda ball: ball.pos.y)
        ]

        if max(column1_sorted, default=-1000) >= max(column2_sorted, default=-1000):
            src_column_index = src_x1
            dest_column_index = src_x2
            src_column = column1_sorted
        else:
            src_column_index = src_x2
            dest_column_index = src_x1
            src_column = column2_sorted

        minpos = src_column.index(max(src_column))

        for _ in range(minpos):
            await move_ball_by_column(
                bc=bc,
                src_x=src_column_index,
                dest_x=dest_column_index,
                claw_index=claw_index,
            )

        await move_ball_by_column(
            bc=bc, src_x=src_column_index, dest_x=dest_x, claw_index=claw_index
        )
