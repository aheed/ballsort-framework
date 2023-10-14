from ball_control_sim import BallControlSim
from ch8_state_manager import Ch8StateManager
from scenario_control import ScenarioControl
from update_reporter import UpdateReporter

class BallControlCh8(BallControlSim, ScenarioControl):

    def __init__(self, update_reporter: UpdateReporter, delay_multiplier: float = 1.0):
        super().__init__(update_reporter=update_reporter, delay_multiplier=delay_multiplier)
        self.state_manager = Ch8StateManager()
