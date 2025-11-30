import uuid

class OperationManager:
    def __init__(self):
        self.ops = {}  # id -> {status, duration}

    def start(self, name, duration):
        op_id = str(uuid.uuid4())
        self.ops[op_id] = {"name": name, "duration": duration, "status": "started"}
        return op_id

    def pause(self, op_id):
        if op_id in self.ops: self.ops[op_id]["status"] = "paused"

    def resume(self, op_id):
        if op_id in self.ops: self.ops[op_id]["status"] = "running"

    def complete(self, op_id):
        if op_id in self.ops: self.ops[op_id]["status"] = "completed"
