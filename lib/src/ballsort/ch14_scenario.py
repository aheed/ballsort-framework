from dataclasses import dataclass, replace
from scenario import Scenario
from state_update_model import (
    StateBall,
    StateModel,
    StatePosition,
    get_default_state,
)


@dataclass
class Ch14Scenario(Scenario):
    """Challenge Implementation"""

    def get_goal_state_description(self) -> str:
        return f"Turn Polish flag 🇵🇱 into Indonesian flag 🇮🇩.\nClaw 0 can operate in columns 0-4. Claw 1 can operate in columns 1-5.\n{self.get_dimensions_description()}"
    
    def get_initial_state(self) -> StateModel:
        
        def build_column(x: int) -> list[StateBall]:
            r_balls = [StateBall(pos=StatePosition(x=x, y=y), color="red") for y in range(3, 5)]
            w_balls = [StateBall(pos=StatePosition(x=x, y=y), color="white") for y in range(1, 3)]
            return r_balls + w_balls
        
        balls: list[StateBall] = []
        max_x = 5
        for x in range(1, max_x): #intentionally leave rightmost and leftmost column empty
            balls = balls + build_column(x=x)

        claw0 = replace(get_default_state().claws[0], max_x = 4)
        claw1 = replace(claw0, pos=StatePosition(x=6, y=0), min_x=1, max_x = 5)
        
        return replace(get_default_state(), balls = balls, max_x=max_x, claws=[claw0, claw1])

    def is_in_goal_state(self, state: StateModel) -> bool:

        # No ball in claw
        if state.claws[0].ball:
            return False
        
        def validate_ball(ball: StateBall) -> bool:
            # no balls in rightmost or leftmost column
            if ball.pos.x > 4 or ball.pos.x == 0:
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

        return all(validate_ball(ball=ball) for ball in state.balls)
    