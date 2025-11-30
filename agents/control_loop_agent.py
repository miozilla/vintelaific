import time
from tools.long_running import OperationManager
from observability.logger import log_event

class ControlLoopAgent:
    def __init__(self, session, bank):
        self.session = session
        self.bank = bank
        self.ops = OperationManager()

    def apply(self, decisions):
        for inter_id, d in decisions.items():
            op_id = self.ops.start(f"intersection_{inter_id}", duration=d["green"] + d["red"])
            log_event("apply_decision", {"inter_id": inter_id, "decision": d, "op_id": op_id})

            # Simulate green phase with pause/resume capability
            self.ops.resume(op_id)
            time.sleep(d["green"] * 0.1)  # fast-forward simulation
            # External trigger example: pause for emergency vehicle
            if self.session.get_flag("emergency"):
                self.ops.pause(op_id)
                log_event("emergency_pause", {"inter_id": inter_id})
                time.sleep(0.2)
                self.ops.resume(op_id)
            time.sleep(d["red"] * 0.1)

            self.ops.complete(op_id)
