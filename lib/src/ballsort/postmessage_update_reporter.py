import asyncio
import json
from dataclasses import asdict
from update_reporter import UpdateReporter
from state_update_model import StateUpdateModel
from IPython.display import display,Javascript



class PostMessageUpdateReporter(UpdateReporter):
    """UpdateReporter using window.postMessage to push updates"""

    client_lock = asyncio.Lock()

    async def send_update(self, stateUpdate: StateUpdateModel):
        async with self.client_lock:
            stringified_obj = json.dumps(asdict(stateUpdate))
            display_obj = Javascript(f"""
                var existingWin = window.bswin;
                existingWin && existingWin.postMessage('{stringified_obj}', "*");    
                """);
            display(display_obj)

    async def shutdown(self):
        pass
