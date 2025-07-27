class BaseAgent:
    def __init__(self, user_context):
        self.user_context = user_context

    def run(self, **kwargs):
        raise NotImplementedError("run should be implemented in subclasses")
