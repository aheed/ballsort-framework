from ball_control import IllegalBallControlStateError
from ball_control_sim import BallControlSim
from ch2_state_manager import Ch2StateManager
from scenario_control import ScenarioControl
from state_update_model import StatePosition
from update_reporter import UpdateReporter

class BallControlCh2(BallControlSim, ScenarioControl):

    ch2_state_manager: Ch2StateManager

    def __init__(self, update_reporter: UpdateReporter, delay_multiplier: float = 1.0):
        super().__init__(update_reporter=update_reporter, delay_multiplier=delay_multiplier)
        self.ch2_state_manager = Ch2StateManager()

    async def read_scales(self) -> int:
        """
        Returns negative if left is heavier, positive if right is heavier, 0 if equal.
        Left scale is the sum of ball weights in columns 2
        Right scale is the sum of ball weights in columns 3
        """

        left_pos = StatePosition(x=2, y=4)
        right_pos = StatePosition(x=3, y=4)
        
        if (self.state.claw.pos == left_pos or self.state.claw.pos == right_pos) and self.state.operating_claw:
            raise IllegalBallControlStateError("Scales can not be used while claw is opening or closing.")
        
        await self._delay(0.3)

        # Hard coded weights
        def get_weight_by_color(color: str) -> int:
            match color:
                case "yellow":
                    return 5
                case "green":
                    return 2
                case "blue":
                    return 1
                case _:
                    return 0
                
        def get_column_weight(x: int) -> int:
            return sum([get_weight_by_color(ball.color) for ball in self.state.balls if ball.pos.x == x])
        
        return get_column_weight(3) - get_column_weight(2)
