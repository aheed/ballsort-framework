from enum import Enum
from asyncio import Event
from dataclasses import dataclass
import sys
sys.path.append("../src/ballsort")

from state_update_model import Claw
from ball_control import BallControl
from test_utils import move_ball_by_column

class SchedMoveStatus(Enum):
    PENDING = 1
    CLAIMED = 2
    GRABBED = 3
    DROPPED = 4

#SchedMoveStatus = Enum('SchedMoveStatus', ['PENDING', 'CLAIMED', 'GRABBED', 'DROPPED'])


@dataclass
class SchedMove:

    #move: tuple[int, int]
    src_x: int
    dest_x: int
    grab_event: Event
    drop_event: Event
    status: SchedMoveStatus

    def __init__(self, move: tuple[int, int]):
        self.src_x, self.dest_x = move
        self.status = SchedMoveStatus.PENDING
        #self.status = Enum('SchedMoveStatus', ['PENDING', 'CLAIMED', 'GRABBED', 'DROPPED'])


class MoveScheduler:

    async def make_moves_single_claw(self, bc: BallControl,  moves: list[tuple[int, int]]):
        for move in moves:
            src_x, dest_x = move
            await move_ball_by_column(bc=bc, src_x=src_x, dest_x=dest_x)

    def __get_move_dependencies(self, sched_moves: list[SchedMove]) -> tuple[dict[int, Event], dict[int, Event]]:
        grab_move_deps: dict[int, Event] = {}
        drop_move_deps: dict[int, Event] = {}
        for i in range(len(sched_moves)):
            # Grab must wait until latest preceding grab or drop in the same column is finished
            for j in range(i-1, -1, -1):
                if sched_moves[j].dest_x == sched_moves[i].src_x:
                    grab_move_deps[i] = sched_moves[j].drop_event
                    break
                if sched_moves[j].src_x == sched_moves[i].src_x:
                    grab_move_deps[i] = sched_moves[j].grab_event
                    break
            
            # Drop must wait until latest preceding grab or drop in the same column is finished
            for j in range(i-1, -1, -1):
                if sched_moves[j].dest_x == sched_moves[i].dest_x:
                    drop_move_deps[i] = sched_moves[j].drop_event
                    break
                if sched_moves[j].src_x == sched_moves[i].dest_x:
                    drop_move_deps[i] = sched_moves[j].grab_event
                    break
            
        return grab_move_deps, drop_move_deps

    async def make_moves_multi_claw(self, bc: BallControl, claws: list[Claw],  moves: list[tuple[int, int]]):

        sched_moves = [SchedMove(move) for move in moves]
        grab_dependencies, drop_dependencies = self.__get_move_dependencies(sched_moves)

        #temp
        for move in moves:
            src_x, dest_x = move
            await move_ball_by_column(bc=bc, src_x=src_x, dest_x=dest_x)

