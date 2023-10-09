import asyncio
import sys

sys.path.append("../src/ballsort")

from ball_control import BallControl
from state_update_model import StatePosition

async def move_ball(bc: BallControl, src: StatePosition, dest: StatePosition):    
    rel_x = src.x - bc.get_position().x
    rel_y = src.y - bc.get_position().y
    await asyncio.gather(
        bc.move_horizontally(rel_x),
        bc.move_vertically(rel_y),
        bc.open_claw())
    await bc.close_claw()
    
    rel_x = dest.x - bc.get_position().x
    rel_y = dest.y - bc.get_position().y
    await asyncio.gather(
        bc.move_horizontally(rel_x),
        bc.move_vertically(rel_y))
    await bc.open_claw()

async def move_ball_by_column(bc: BallControl, src_x: int, dest_x: int):
    src_column_top_occupied_y = min([ball.pos.y for ball in bc.get_state().balls if ball.pos.x == src_x],default=bc.get_state().max_y)
    dest_column_top_vacant_y = min([ball.pos.y for ball in bc.get_state().balls if ball.pos.x == dest_x],default=bc.get_state().max_y + 1) - 1
    await move_ball(bc=bc, src=StatePosition(x=src_x, y=src_column_top_occupied_y), dest=StatePosition(x=dest_x, y=dest_column_top_vacant_y))