import math

class CodeExecTool:
    def run(self, snippet: str, inputs: dict):
        # Strictly whitelisted operations (mock). Demonstrates “tool call”.
        if snippet == "queue_length":
            q = inputs.get("arrivals", 0) - inputs.get("departures", 0)
            return {"queue": max(q, 0)}
        if snippet == "eta":
            rate = inputs.get("rate", 1)
            return {"eta": round(1.0 / max(rate, 1e-6), 3)}
        return {"error": "unsupported"}
