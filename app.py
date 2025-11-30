import yaml
import time
from agents.coordinator import Coordinator
from memory.session_service import InMemorySessionService
from memory.memory_bank import MemoryBank
from observability.logger import log_event
from evaluation.policy_eval import evaluate

def main():
    # Load configuration for intersections and lanes
    cfg = yaml.safe_load(open("env/config.yaml"))

    # Initialize session + long-term memory
    session = InMemorySessionService(session_id="demo-001")
    bank = MemoryBank(max_episodes=50)

    # Coordinator orchestrates vision → policy → control loop
    coord = Coordinator(cfg["intersections"], session, bank)

    # Run multiple cycles
    for cycle in range(5):
        timestamps = {"t_obs_start": time.time()}

        # Collect observations (parallel vision agents)
        observations = coord.collect_observations()
        timestamps["t_obs_end"] = time.time()

        # Policy agent decides (sequential)
        decisions = coord.policy.plan(observations)
        timestamps["t_policy_end"] = time.time()

        # Control loop applies (loop agent, pause/resume supported)
        coord.controller.apply(decisions)
        timestamps["t_apply_end"] = time.time()

        # Evaluate cycle performance
        report = evaluate(observations, decisions, timestamps)
        log_event("evaluation_report", {"cycle": cycle, "report": report})

        # Simulate emergency event mid-run
        if cycle == 2:
            session.set_flag("emergency", True)
            log_event("emergency_flag_set", {"cycle": cycle})
        else:
            session.set_flag("emergency", False)

        log_event("cycle_complete", {"cycle": cycle})

if __name__ == "__main__":
    main()
