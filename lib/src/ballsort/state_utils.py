from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
)


def is_ball_in_claw(state: StateModel) -> bool:
    return not not state.claw.ball_color


def is_ball_at_current_pos(state: StateModel) -> bool:
    return next(
        (True for ball in state.balls if ball.pos == state.claw.pos),
        False,
    )
    # balls_at_current_pos = filter(lambda ball: ball.pos == self.state.claw.pos, self.state.balls)
    # return any(balls_at_current_pos)

def get_ball_at(state: StateModel, pos: StatePosition) -> StateBall | None:
    return next(
        (ball for ball in state.balls if pos == ball.pos),
        None,
    )

def get_ball_at_current_pos(state: StateModel) -> StateBall | None:
    return next(
        (ball for ball in state.balls if ball.pos == state.claw.pos),
        None,
    )

def get_top_occupied_index(state: StateModel) -> int:
    y_indexes_in_current_column = [
        ball.pos.y for ball in state.balls if ball.pos.x == state.claw.pos.x
    ]
    top_occupied_y_index = (
        min(y_indexes_in_current_column) if y_indexes_in_current_column else state.max_y + 1
    )
    return top_occupied_y_index


def get_top_vacant_index(state: StateModel) -> int:
    return get_top_occupied_index(state) - 1
