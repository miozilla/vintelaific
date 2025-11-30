class MemoryBank:
    def __init__(self, max_episodes=100):
        self.episodes = []
        self.max_episodes = max_episodes

    def append_episode(self, observations, decisions):
        self.episodes.append({"obs": observations, "dec": decisions})
        if len(self.episodes) > self.max_episodes:
            self.context_compact()

    def context_compact(self):
        # Compact: keep recent, summarize older (min/max/avg per intersection)
        if len(self.episodes) <= 10: return
        older = self.episodes[:-10]
        summary = {}
        for ep in older:
            for k, counts in ep["obs"].items():
                summary.setdefault(k, []).append(sum(counts))
        agg = {k: {"min": min(v), "max": max(v), "avg": sum(v)/len(v)} for k, v in summary.items()}
        self.episodes = [{"summary": agg}] + self.episodes[-10:]
