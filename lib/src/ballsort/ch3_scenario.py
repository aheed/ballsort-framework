from dataclasses import dataclass, replace
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch3Scenario(Scenario):
    """Challenge Implementation"""

    def get_goal_state_description(self) -> str:
        return f"Turn Polish flag 🇵🇱 into Indonesian flag 🇮🇩.\n{self.get_dimensions_description()}"
    
    def get_initial_state(self) -> StateModel:
        
        def build_column(x: int) -> list[StateBall]:
            r_balls = [StateBall(pos=StatePosition(x=x, y=y), color="red") for y in range(3, 5)]
            w_balls = [StateBall(pos=StatePosition(x=x, y=y), color="white") for y in range(1, 3)]
            return r_balls + w_balls
        
        balls: list[StateBall] = []
        max_x = 4
        for x in range(max_x): #intentionally leave rightmost column empty
            balls = balls + build_column(x=x)
        
        return replace(get_default_state(), balls = balls, max_x=max_x)

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in claw
        if state.claw.ball_color:
            return False
        
        def validate_ball(ball: StateBall) -> bool:
            # no balls in rightmost column
            if ball.pos.x > 3:
                return False

            # no higher column than 4    
            if ball.pos.y < 1:
                return False

            # all red balls on high y coordinates    
            if ball.color == "red" and ball.pos.y > 2:
                return False

            # all white balls on low y coordinates    
            if ball.color == "white" and ball.pos.y < 3:
                return False

            return True

        return not next((True for ball in state.balls if not validate_ball(ball)), False)
    
    