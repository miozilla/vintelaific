from agents.vision_agent import VisionAgent
from agents.policy_agent import PolicyAgent
from agents.control_loop_agent import ControlLoopAgent
from memory.session_service import InMemorySessionService
from memory.memory_bank import MemoryBank
from observability.logger import log_event

class Coordinator:
    def __init__(self, intersections, session: InMemorySessionService, bank: MemoryBank):
        self.intersections = intersections
        self.session = session
        self.bank = bank
        self.policy = PolicyAgent(session, bank)
        self.controller = ControlLoopAgent(session, bank)

    def run_cycle(self):
        # Parallel: fan-out vision agents per intersection/lane
        observations = {}
        for inter_id, inter_cfg in self.intersections.items():
            observations[inter_id] = []
            agents = [VisionAgent(lane_cfg) for lane_cfg in inter_cfg["lanes"]]
            lane_counts = [agent.observe() for agent in agents]  # pseudo-parallel; swap with threads/async if desired
            observations[inter_id] = lane_counts
        log_event("observations_collected", {"obs": observations})

        # Sequential: policy decision
        decisions = self.policy.plan(observations)
        log_event("policy_decisions", {"decisions": decisions})

        # Loop agent: apply and monitor
        self.controller.apply(decisions)
        self.bank.append_episode(observations, decisions)
