from observability.logger import log_event

'''
class PolicyAgent:
    def __init__(self, session, bank):
        self.session = session
        self.bank = bank

    def plan(self, observations):
        # LLM-powered stub: transform observations -> timing policy
        # Replace with real LLM for richer agentic reasoning if desired.
        decisions = {}
        for inter_id, counts in observations.items():
            total = sum(counts)
            # Simple heuristic: base + min(total, cap)
            base_green = 5
            dynamic = base_green + min(total, 10)
            decisions[inter_id] = {"green": dynamic, "red": 5, "phase": "NS" if counts[0] >= counts[1] else "EW"}
        log_event("policy_planned", {"decisions": decisions})
        return decisions
'''

# Enhanced PolicyAgent with Emergency Override

class PolicyAgent:
    def __init__(self, session, bank):
        self.session = session
        self.bank = bank

    def plan(self, observations):
        """
        observations: dict of {junction_id: {"counts": [lane_counts], "emergency": bool}}
        """
        decisions = {}

        for inter_id, obs in observations.items():
            counts = obs.get("counts", [])
            emergency = obs.get("emergency", False)

            if emergency:
                # 🚑 Emergency override: immediate priority
                decisions[inter_id] = {
                    "green": 15,   # extended green for clearance
                    "red": 0,      # skip red
                    "phase": "EMERGENCY"
                }
                log_event("emergency_override", {"junction": inter_id})
                continue

            # Normal queue-based logic
            total = sum(counts)
            base_green = 5
            dynamic = base_green + min(total, 10)

            # Simple heuristic: choose NS vs EW based on lane comparison
            phase = "NS" if counts and counts[0] >= (counts[1] if len(counts) > 1 else 0) else "EW"

            decisions[inter_id] = {
                "green": dynamic,
                "red": 5,
                "phase": phase
            }

        log_event("policy_planned", {"decisions": decisions})
        return decisions
