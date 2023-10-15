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
        goal_accomplished = self.scenario.is_in_goal_state(state)
        if (goal_accomplished and not state.goal_accomplished):
            print("Goal accomplished! 😁")
        state.goal_accomplished = goal_accomplished
        return state

    def set_scenario(self, state: StateModel, scenario: Scenario) -> StateModel:
        self.scenario = scenario
        state = scenario.get_initial_state()
        print(f"Goal:\n{scenario.get_goal_state_description()}")
        return state

    def _move_relative(self, state: StateModel, x: int, y: int, claw_index: int) -> StateModel:
        newX = state.claws[claw_index].pos.x + x
        newY = state.claws[claw_index].pos.y + y
        newClawState = replace(state.claws[claw_index], pos=StatePosition(x = newX, y = newY))
        state.claws[claw_index] = newClawState
        #print(f"new position: {newX}, {newY}")
        return state

    def move_horizontally_start(self, state: StateModel, distance: int, claw_index: int) -> StateModel:
        self.validator.move_horizontally(state=state, distance=distance, claw_index=claw_index)
        state.claws[claw_index].moving_horizontally = True
        return self._move_relative(state=state,x=distance, y=0, claw_index=claw_index)
    
    def move_horizontally_end(self, state: StateModel, claw_index: int) -> StateModel:
        state.claws[claw_index].moving_horizontally = False
        return state

    def move_vertically_start(self, state: StateModel, distance: int, claw_index: int) -> StateModel:
        self.validator.move_vertically(state=state, distance=distance, claw_index=claw_index)
        state.claws[claw_index].moving_vertically = True
        return self._move_relative(state=state, x=0, y=distance, claw_index=claw_index)

    def move_vertically_end(self, state: StateModel, claw_index: int) -> StateModel:
        state.claws[claw_index].moving_vertically = False
        return state

    def open_claw_start(self, state: StateModel, claw_index: int) -> StateModel:
        self.validator.open_claw(state, claw_index=claw_index)
        state.claws[claw_index].operating_claw = True
        state.claws[claw_index].open = True
        #print(f"opening claw")
        if not is_ball_in_claw(state, claw_index=claw_index):
            return state
        print(f"dropping at {state.claws[claw_index].pos}")
        newBall = StateBall(pos=state.claws[claw_index].pos, color=state.claws[claw_index].ball_color, value=state.claws[claw_index].ball_value, label=state.claws[claw_index].ball_label)
        state.claws[claw_index].ball_color = ""
        state.claws[claw_index].ball_value = 0 #not strictly necessary
        state.claws[claw_index].ball_label = "" #not strictly necessary
        state.balls.append(newBall)
        return self._check_goal_state(state)

    def close_claw_start(self, state: StateModel, claw_index: int) -> StateModel:
        self.validator.close_claw(state, claw_index=claw_index)
        state.claws[claw_index].operating_claw = True
        state.claws[claw_index].open = False
        #print(f"closing claw")
        ball_to_grab = get_ball_at_current_pos(state, claw_index=claw_index)
        if not ball_to_grab:
            return state
        print(f"grabbing {ball_to_grab} at {state.claws[claw_index].pos}")
        state.claws[claw_index].ball_color = ball_to_grab.color
        state.claws[claw_index].ball_value = ball_to_grab.value
        state.claws[claw_index].ball_label = ball_to_grab.label
        #remove ball from list
        state.balls = [ball for ball in state.balls if ball.pos != ball_to_grab.pos]
        return self._check_goal_state(state)

    def open_claw_end(self, state: StateModel, claw_index: int) -> tuple[StateModel, bool]:
        droppedBall = next((ball for ball in state.balls if ball.pos == state.claws[claw_index].pos), None)
        
        newState = state
        newState.claws[claw_index].operating_claw = False

        if not droppedBall or not self.scenario:
            return newState, False
        
        return self.scenario.on_ball_dropped(state, droppedBall)

    def close_claw_end(self, state: StateModel, claw_index: int) -> StateModel:
        state.claws[claw_index].operating_claw = False
        return state
