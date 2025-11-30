import time
import uuid

RUN_ID = str(uuid.uuid4())

def log_event(name, payload):
    ts = time.time()
    print(f"[run={RUN_ID} ts={ts:.3f} event={name}] {payload}")
