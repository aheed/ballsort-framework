from enum import Enum
import asyncio
from asyncio import Event, Lock
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

@dataclass
class SchedMove:
    src_x: int
    dest_x: int
    grab_event: Event
    drop_event: Event
    status: SchedMoveStatus

    def __init__(self, move: tuple[int, int]):
        self.src_x, self.dest_x = move
        self.status = SchedMoveStatus.PENDING
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
    
    async def __schedule_claw(self, bc: BallControl, claw_index: int, min_x: int, max_x: int, home_x:int, sched_moves: list[SchedMove], column_locks: list[Lock], timeout_sec: float) -> None:
        
        grab_dependencies, drop_dependencies = self.__get_move_dependencies(sched_moves)        

        ongoing_move_index: int | None = None
        ball_in_claw = False
        

        def is_good_move(index: int) -> bool:
            sched_move = sched_moves[index]
            if sched_move.status != SchedMoveStatus.PENDING:
                return False
            
            if sched_move.src_x < min_x or sched_move.src_x > max_x or sched_move.dest_x < min_x or sched_move.dest_x > max_x:
                return False
            
            return True
        
        #async def go_home():
        #    await go_to_pos(bc=bc, dest=StatePosition(x=home_x, y=0), claw_index=claw_index, open_claw=False)

        def get_columns_to_access(current_x:int, dest_x: int) -> list[int]:
            """Returns an ordered list of columns to which access is needed for a move"""
            if dest_x > current_x:
                col_range = range(current_x + 1, dest_x + 1)
            else:
                col_range = range(current_x - 1, dest_x - 1, -1)
            #return  [x for x in range(min(current_x, dest_x), max(current_x, dest_x) + 1) if x != current_x]
            return [x for x in col_range]

        async def acquire_columns(columns: list[int]):
            #print("acquiring columns", columns)
            accessed_columns: list[int] = []
            for x in columns:
                try:
                    await asyncio.wait_for(column_locks[x].acquire(), timeout=timeout_sec)
                    print(claw_index, "got col", x)
                    accessed_columns.append(x)
                except TimeoutError:
                    print(claw_index, 'timeout!')
                    for accessed_column in accessed_columns:
                        column_locks[accessed_column].release()
                        print(claw_index, "rel col", accessed_column, "because of timeout")
                    raise TimeoutError
                
        def release_columns(columns: list[int]):
            #print("releasing columns", columns)
            for x in columns:
                column_locks[x].release()
                print(claw_index, "rel col", x)

        async def go_to_pos_exclusive(bc: BallControl, dest: StatePosition, open_claw: bool, claw_index: int = 0):
            origin_x = bc.get_state().claws[claw_index].pos.x
            columns_to_acquire = get_columns_to_access(current_x=origin_x, dest_x=dest.x)
            await acquire_columns(columns=columns_to_acquire)
            await go_to_pos(bc=bc, dest=dest, open_claw=open_claw, claw_index=claw_index)
            columns_to_release = [x for x in columns_to_acquire if x != dest.x] + ([origin_x] if origin_x != dest.x else [])
            release_columns(columns=columns_to_release)

        async def go_home_exclusive():
            print(claw_index, "go home to col", home_x)
            await go_to_pos_exclusive(bc=bc, dest=StatePosition(x=home_x, y=0), claw_index=claw_index, open_claw=False)

        # claim access to the current column. Should not fail.
        await column_locks[bc.get_state().claws[claw_index].pos.x].acquire()

        while True:
            # Find a suitable move to execute
            #  If you have a ball in the claw then continue with the ongoing move
            if ongoing_move_index is None:
                ongoing_move_index = next((i for i in range(len(sched_moves)) if is_good_move(index=i)), None)                

            if ongoing_move_index is None:
                #  There are no more possible moves. Go to home column, then die.
                print(claw_index, "no more possible moves. Curl up and die.")
                await go_home_exclusive()
                break

            if sched_moves[ongoing_move_index].status == SchedMoveStatus.PENDING:
                print(claw_index, "claiming move", ongoing_move_index)
                sched_moves[ongoing_move_index].status = SchedMoveStatus.CLAIMED
            
            sched_move = sched_moves[ongoing_move_index]

            try:
                if ball_in_claw:
                    if e := drop_dependencies.get(ongoing_move_index):
                        print(claw_index, "waiting for event before drop", e)
                        await asyncio.wait_for(e.wait(), timeout=timeout_sec)

                    await go_to_pos_exclusive(bc=bc, dest=get_column_top_vacant_pos(bc=bc, x=sched_move.dest_x), open_claw=False, claw_index=claw_index)
                    await bc.open_claw(claw_index=claw_index)
                    sched_moves[ongoing_move_index].status = SchedMoveStatus.DROPPED
                    print(claw_index, "setting drop event", sched_moves[ongoing_move_index].drop_event)
                    sched_moves[ongoing_move_index].drop_event.set()
                    ball_in_claw = False
                    ongoing_move_index = None
                else:
                    if e := grab_dependencies.get(ongoing_move_index):
                        print(claw_index, "waiting for event before grab", e)
                        await asyncio.wait_for(e.wait(), timeout=timeout_sec)

                    await go_to_pos_exclusive(bc=bc, dest=get_column_top_occupied_pos(bc=bc, x=sched_move.src_x), open_claw=True, claw_index=claw_index)
                    await bc.close_claw(claw_index=claw_index)
                    sched_moves[ongoing_move_index].status = SchedMoveStatus.GRABBED
                    print(claw_index, "setting grab event", sched_moves[ongoing_move_index].grab_event)
                    sched_moves[ongoing_move_index].grab_event.set()
                    ball_in_claw = True
            except TimeoutError:
                    print(claw_index, "Waiting for move access timed out. Move out of the way to avoid possible deadlock.")
                    await go_home_exclusive()
                    continue

    async def make_moves_multi_claw(self, bc: BallControl, claws: list[Claw], moves: list[tuple[int, int]], timeout_sec: float):
        """Assumes two claws for now"""
        #claw_routines = [self.__schedule_claw(claw_index=i, min_x=claws[i].min_x, max_x=claws[i].max_x, moves=moves) for i in range(len(claws))]
        #await asyncio.gather(*claw_routines)

        column_locks = [Lock() for _ in range(bc.get_state().max_x+1)]
        sched_moves = [SchedMove(move) for move in moves]

         # claws should have different timeouts to avoid livelock
        timeout_sec0 = timeout_sec * 1.3
        timeout_sec1 = timeout_sec * 1.0

        claw0_routine = self.__schedule_claw(bc=bc, claw_index=0, min_x=claws[0].min_x, max_x=claws[0].max_x, home_x=claws[0].min_x, sched_moves=sched_moves, column_locks=column_locks, timeout_sec=timeout_sec0)
        claw1_routine = self.__schedule_claw(bc=bc, claw_index=1, min_x=claws[1].min_x, max_x=claws[1].max_x, home_x=claws[1].max_x, sched_moves=sched_moves, column_locks=column_locks, timeout_sec=timeout_sec1)

        #await claw0_routine #temp
        #await claw1_routine #temp
        await asyncio.gather(claw0_routine, claw1_routine)
        #await asyncio.gather(claw0_routine)

