from state_update_model import StateUpdateModel

class UpdateReporter(object):
    """Interface for reporting state"""

    async def send_update(self, stateUpdate: StateUpdateModel):
        """Report state update"""
        pass

    async def shutdown(self):
        """Any cleanup to do before the object is disposed"""
        pass