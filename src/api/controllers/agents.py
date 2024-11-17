from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.entities.agent import AgentType
from src.db.errors.agent import AgentNotFoundError, CriticizedAgentNotFoundError
from src.db.errors.graph import GraphNotFoundError
from src.db.errors.prompt import PromptNotFoundError
from src.db.errors.settings import SettingsNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.agent_service import AgentService
from src.models.agent import (
    CreateUpdateAgentModel,
    CreateUpdateAIAgentModel,
    CreateUpdateChatAgentModel,
    CreateUpdateCriticAgentModel,
    CreateUpdateHardCodeAgentModel,
    ExtendedAgentModel,
)

router = APIRouter(prefix="/graphs/{graph_id}/agents")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except GraphNotFoundError:
            raise HTTPException(status_code=404, detail="Graph not found")
        except CriticizedAgentNotFoundError:
            raise HTTPException(status_code=404, detail="Criticized agent not found")
        except AgentNotFoundError:
            raise HTTPException(status_code=404, detail="Agent not found")
        except SettingsNotFoundError:
            raise HTTPException(status_code=404, detail="Settings not found")
        except PromptNotFoundError:
            raise HTTPException(status_code=404, detail="Prompt not found")

    return wrapper


@router.post("/ai")
@map_errors
def create_ai_agent(
    graph_id: int,
    body: CreateUpdateAIAgentModel,
    token: str = Depends(get_token),
) -> list[ExtendedAgentModel]:
    """
    Create AI agent.

    Args:
        graph_id: int - Graph id
        body: CreateUpdateAIAgentModel - Agent data
        token: str - Authentication token

    Returns:
        list[ExtendedAgentModel] - List of agents

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Settings not found"): If the settings not found
        HTTPException(404, detail="Prompt not found"): If the prompt not found
    """
    return AgentService.create_agent(graph_id, AgentType.ai, body, token)


@router.post("/hard_code")
@map_errors
def create_hard_code_agent(
    graph_id: int,
    body: CreateUpdateHardCodeAgentModel,
    token: str = Depends(get_token),
) -> list[ExtendedAgentModel]:
    """
    Create hard-coded agent.

    Args:
        graph_id: int - Graph id
        body: CreateUpdateHardCodeAgentModel - Agent data
        token: str - Authentication token

    Returns:
        list[ExtendedAgentModel] - List of agents

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
    """
    return AgentService.create_agent(graph_id, AgentType.hard_code, body, token)


@router.post("/chat")
@map_errors
def create_chat_agent(
    graph_id: int,
    body: CreateUpdateChatAgentModel,
    token: str = Depends(get_token),
) -> list[ExtendedAgentModel]:
    """
    Create chat agent.

    Args:
        graph_id: int - Graph id
        body: CreateUpdateChatAgentModel - Agent data
        token: str - Authentication token

    Returns:
        list[ExtendedAgentModel] - List of agents

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Settings not found"): If the settings not found
        HTTPException(404, detail="Prompt not found"): If the prompt not found
    """
    return AgentService.create_agent(graph_id, AgentType.chat, body, token)


@router.post("/critic")
@map_errors
def create_critic_agent(
    graph_id: int,
    body: CreateUpdateCriticAgentModel,
    token: str = Depends(get_token),
) -> list[ExtendedAgentModel]:
    """
    Create critic agent.

    Args:
        graph_id: int - Graph id
        body: CreateUpdateCriticAgentModel - Agent data
        token: str - Authentication token

    Returns:
        list[ExtendedAgentModel] - List of agents

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Settings not found"): If the settings not found
        HTTPException(404, detail="Prompt not found"): If the prompt not found
        HTTPException(404, detail="Criticized agent not found"): If the criticized agent not found
    """
    return AgentService.create_agent(graph_id, AgentType.critic, body, token)


@router.get("/")
@map_errors
def get_agents(
    graph_id: int,
    token: str = Depends(get_token),
) -> list[ExtendedAgentModel]:
    """
    Get all agents of graph.

    Args:
        graph_id: int - Graph id
        token: str - Authentication token

    Returns:
        list[ExtendedAgentModel] - List of agents

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
    """
    return AgentService.get_agents(graph_id, token)


@router.get("/{agent_id}")
@map_errors
def get_agent(
    graph_id: int,
    agent_id: int,
    token: str = Depends(get_token),
) -> ExtendedAgentModel:
    """
    Get agent info.

    Args:
        graph_id: int - Graph id
        agent_id: int - Agent id
        token: str - Authentication token

    Returns:
        ExtendedAgentModel - Agent

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Agent not found"): If the agent not found
    """
    return AgentService.get_agent(graph_id, agent_id, token)


@router.delete("/{agent_id}")
@map_errors
def delete_agent(
    graph_id: int,
    agent_id: int,
    token: str = Depends(get_token),
):
    """
    Delete agent.

    Args:
        graph_id: int - Graph id
        agent_id: int - Agent id
        token: str - Authentication token

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Agent not found"): If the agent not found
    """
    AgentService.delete_agent(graph_id, agent_id, token)


@router.put("/{agent_id}")
@map_errors
def update_agent(
    graph_id: int,
    agent_id: int,
    body: CreateUpdateAgentModel,
    token: str = Depends(get_token),
):
    """
    Update agent.

    Args:
        graph_id: int - Graph id
        agent_id: int - Agent id
        body: CreateUpdateAgentModel - Agent data
        token: str - Authentication token

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Agent not found"): If the agent not found
    """
    AgentService.update_agent(graph_id, agent_id, body, token)
