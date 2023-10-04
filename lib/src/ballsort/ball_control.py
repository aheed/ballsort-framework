from scenario import ScenarioProgress
from state_update_model import StateModel, StatePosition


class IllegalBallControlStateError(Exception):
    "Raised when a control command is issued while a command for movement along the same axis is still being executed"
    pass

class BallControl(object):
    """Interface for controlling a ball manipulator in a grid"""

    async def __aenter__(self):
        pass
    
    async def __aexit__(self, *_):
        pass

    async def move_horizontally(self, distance: int):
        """Move the claw horizontally"""
        pass

    async def move_vertically(self, distance: int):
        """Move the claw vertically"""
        pass

    async def open_claw(self):
        pass

    async def close_claw(self):
        pass

    def get_position(self) -> StatePosition:
        raise NotImplementedError
    
    def get_progress(self) -> ScenarioProgress:
        """Returns progress toward goal state."""
        raise NotImplementedError

    def is_in_goal_state(self) -> bool:
        """Returns true only if state fulfills the goal state criteria."""
        raise NotImplementedError
    
    def get_state(self) -> StateModel:
        """Returns the complete state of the board."""
        raise NotImplementedError
