from scenario import Scenario
#from state_update_model import StateBall

class ScenarioControl(object):
    """Interface for populating a grid"""

    async def set_scenario(self, scenario: Scenario):
        pass