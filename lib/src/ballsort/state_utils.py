from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
)


def is_ball_in_claw(state: StateModel, claw_index: int) -> bool:
    return not not state.claws[claw_index].ball_color


def is_ball_at_current_pos(state: StateModel, claw_index: int) -> bool:
    return next(
        (True for ball in state.balls if ball.pos == state.claws[claw_index].pos),
        False,
    )
    # balls_at_current_pos = filter(lambda ball: ball.pos == self.state.claw.pos, self.state.balls)
    # return any(balls_at_current_pos)

def get_ball_at(state: StateModel, pos: StatePosition) -> StateBall | None:
    return next(
        (ball for ball in state.balls if pos == ball.pos),
        None,
    )

def get_ball_at_current_pos(state: StateModel, claw_index: int) -> StateBall | None:
    return next(
        (ball for ball in state.balls if ball.pos == state.claws[claw_index].pos),
        None,
    )

def get_top_occupied_index(state: StateModel, claw_index: int) -> int:
    y_indexes_in_current_column = [
        ball.pos.y for ball in state.balls if ball.pos.x == state.claws[claw_index].pos.x
    ]
    top_occupied_y_index = (
        min(y_indexes_in_current_column) if y_indexes_in_current_column else state.max_y + 1
    )
    return top_occupied_y_index


def get_top_vacant_index(state: StateModel, claw_index: int) -> int:
    return get_top_occupied_index(state, claw_index=claw_index) - 1
