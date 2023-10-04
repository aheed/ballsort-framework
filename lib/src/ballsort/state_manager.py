from dataclasses import dataclass, replace
from scenario import Scenario
from state_utils import get_ball_at_current_pos, is_ball_in_claw
from state_validator import StateValidator
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
)


@dataclass
class StateManager:
    """Validates operations and keeps state up to date"""

    validator: StateValidator
    scenario: Scenario | None

    def __init__(self, scenario : Scenario | None = None):
        self.validator = StateValidator()
        self.scenario = scenario

    def _check_goal_state(self, state: StateModel) -> StateModel:
        if self.scenario is None:
            return state
        isInGoalState = self.scenario.is_in_goal_state(state)
        if (isInGoalState and not state.isInGoalState):
            print("Goal accomplished! 😁")
        state.isInGoalState = isInGoalState
        return state

    def set_scenario(self, state: StateModel, scenario: Scenario) -> StateModel:
        self.scenario = scenario
        state = scenario.get_initial_state()
        print(f"Goal:\n{scenario.get_goal_state_description()}")
        return state

    def _move_relative(self, state: StateModel, x: int, y: int) -> StateModel:
        newX = state.claw.pos.x + x
        newY = state.claw.pos.y + y
        state = replace(state, claw=replace(state.claw, pos=StatePosition(x = newX, y = newY)))
        #print(f"new position: {newX}, {newY}")
        return state

    def move_horizontally_start(self, state: StateModel, distance: int) -> StateModel:
        self.validator.move_horizontally(state=state, distance=distance)
        state.moving_horizontally = True
        return self._move_relative(state=state,x=distance, y=0)
    
    def move_horizontally_end(self, state: StateModel) -> StateModel:
        state.moving_horizontally = False
        return state

    def move_vertically_start(self, state: StateModel, distance: int) -> StateModel:
        self.validator.move_vertically(state=state, distance=distance)
        state.moving_vertically = True
        return self._move_relative(state=state, x=0, y=distance)

    def move_vertically_end(self, state: StateModel) -> StateModel:
        state.moving_vertically = False
        return state

    def open_claw_start(self, state: StateModel) -> StateModel:
        self.validator.open_claw(state)
        state.operating_claw = True
        state.claw.open = True
        #print(f"opening claw")
        if not is_ball_in_claw(state):
            return state
        print(f"dropping at {state.claw.pos}")
        newBall = StateBall(pos=state.claw.pos, color=state.claw.ball_color, value=state.claw.ball_value, label=state.claw.ball_label)
        state.claw.ball_color = ""
        state.claw.ball_value = 0 #not strictly necessary
        state.claw.ball_label = "" #not strictly necessary
        state.balls.append(newBall)
        return self._check_goal_state(state)

    def close_claw_start(self, state: StateModel) -> StateModel:
        self.validator.close_claw(state)
        state.operating_claw = True
        state.claw.open = False
        #print(f"closing claw")
        ball_to_grab = get_ball_at_current_pos(state)
        if not ball_to_grab:
            return state
        print(f"grabbing {ball_to_grab} at {state.claw.pos}")
        state.claw.ball_color = ball_to_grab.color
        state.claw.ball_value = ball_to_grab.value
        state.claw.ball_label = ball_to_grab.label
        #remove ball from list
        state.balls = [ball for ball in state.balls if ball.pos != ball_to_grab.pos]
        return self._check_goal_state(state)

    def open_claw_end(self, state: StateModel) -> StateModel:
        state.operating_claw = False
        return state

    def close_claw_end(self, state: StateModel) -> StateModel:
        state.operating_claw = False
        return state
