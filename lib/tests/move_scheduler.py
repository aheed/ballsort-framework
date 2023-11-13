from enum import Enum
import asyncio
from asyncio import Event
from dataclasses import dataclass
import sys
sys.path.append("../src/ballsort")

from state_update_model import Claw, StatePosition
from ball_control import BallControl
from test_utils import get_column_top_occupied_pos, get_column_top_vacant_pos, go_to_pos, move_ball_by_column

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
        self.grab_event = Event()
        self.drop_event = Event()

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
    
    async def __schedule_claw(self, bc: BallControl, claw_index: int, min_x: int, max_x: int, home_x:int, moves: list[tuple[int, int]]) -> None:
        sched_moves = [SchedMove(move) for move in moves]
        grab_dependencies, drop_dependencies = self.__get_move_dependencies(sched_moves)

        ongoing_move_index: int | None = None
        ball_in_claw = False

        def is_good_move(index: int) -> bool:
            sched_move = sched_moves[index]
            if sched_move.status != SchedMoveStatus.PENDING:
                return False
            
            if sched_move.src_x < min_x or sched_move.src_x > max_x or sched_move.dest_x < min_x or sched_move.dest_x > max_x:
                return False
            
            return True #temp
        
        async def go_home():
            await go_to_pos(bc=bc, dest=StatePosition(x=home_x, y=0), claw_index=claw_index, open_claw=False)

        while True:
            # Find a suitable move to execute
            #  If you have a ball in the claw then continue with the ongoing move
            if ongoing_move_index is None:
                ongoing_move_index = next((i for i in range(len(sched_moves)) if is_good_move(index=i)), None)                

            if ongoing_move_index is None:
                #  There are no more possible moves. Go to home column, then die.
                await go_home()    
                break

            if sched_moves[ongoing_move_index].status == SchedMoveStatus.PENDING:
                sched_moves[ongoing_move_index].status = SchedMoveStatus.CLAIMED
            
            sched_move = sched_moves[ongoing_move_index]

            if ball_in_claw:
                #  await dependency
                if e := drop_dependencies.get(ongoing_move_index):
                    await e.wait()
                
                #  await column access

                #  execute
                await go_to_pos(bc=bc, dest=get_column_top_vacant_pos(bc=bc, x=sched_move.dest_x), open_claw=False, claw_index=claw_index)
                await bc.open_claw(claw_index=claw_index)
                sched_moves[ongoing_move_index].status = SchedMoveStatus.DROPPED
                sched_moves[ongoing_move_index].drop_event.set()
                ball_in_claw = False
                ongoing_move_index = None
            else:
                #  await dependency
                if e := grab_dependencies.get(ongoing_move_index):
                    await e.wait()
                
                #  await column access

                #  execute
                await go_to_pos(bc=bc, dest=get_column_top_occupied_pos(bc=bc, x=sched_move.src_x), open_claw=True, claw_index=claw_index)
                await bc.close_claw(claw_index=claw_index)
                sched_moves[ongoing_move_index].status = SchedMoveStatus.GRABBED
                sched_moves[ongoing_move_index].grab_event.set()
                ball_in_claw = True

            #  On timeout: go to home column (unless you are "master"?)

    async def make_moves_multi_claw(self, bc: BallControl, claws: list[Claw], moves: list[tuple[int, int]]):
        """Assumes two claws for now"""
        #claw_routines = [self.__schedule_claw(claw_index=i, min_x=claws[i].min_x, max_x=claws[i].max_x, moves=moves) for i in range(len(claws))]
        #await asyncio.gather(*claw_routines)

        claw0_routine = self.__schedule_claw(bc=bc, claw_index=0, min_x=claws[0].min_x, max_x=claws[0].max_x, home_x=claws[0].min_x, moves=moves)
        #claw1_routine = self.__schedule_claw(bc=bc, claw_index=1, min_x=claws[1].min_x, max_x=claws[1].max_x, home_x=claws[1].max_x, moves=moves)

        await claw0_routine #temp
        #await asyncio.gather(claw0_routine, claw1_routine)

