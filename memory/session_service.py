class InMemorySessionService:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = {"flags": {}, "last_decisions": {}}

    def set_flag(self, key, value=True):
        self.state["flags"][key] = value

    def get_flag(self, key):
        return self.state["flags"].get(key, False)

    def set_decisions(self, decisions):
        self.state["last_decisions"] = decisions

    def get_decisions(self):
        return self.state["last_decisions"]
