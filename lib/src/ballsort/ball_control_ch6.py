from ball_control_sim import BallControlSim
from ch6_state_manager import Ch6StateManager
from scenario_control import ScenarioControl
from update_reporter import UpdateReporter

class BallControlCh6(BallControlSim, ScenarioControl):

    def __init__(self, update_reporter: UpdateReporter, delay_multiplier: float = 1.0):
        super().__init__(update_reporter=update_reporter, delay_multiplier=delay_multiplier)
        self.state_manager = Ch6StateManager()
