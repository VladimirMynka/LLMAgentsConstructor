class AgentNotFoundError(Exception):
    pass


class CriticizedAgentNotFoundError(AgentNotFoundError):
    pass


class InvalidAgentTypeError(Exception):
    pass

