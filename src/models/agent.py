from pydantic import BaseModel

from src.db.entities.agent import AgentType
from src.models.agent_details import (
    AgentDetails,
    CreateUpdateAgentDetails,
    CriticDetails,
)
from src.models.node import CreateNodeRequestModel, NodeModel


class AgentModel(BaseModel):
    """
    Agent model.
    """

    id: int
    name: str
    agent_type: AgentType
    description: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Agent1",
                "agent_type": AgentType.ai,
                "description": "Agent1 description",
            }
        }


class ExtendedAgentModel(AgentModel):
    """
    Extended agent model.
    """

    start_log_message: str
    finish_log_message: str
    details: AgentDetails
    node: NodeModel

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Agent1",
                "agent_type": AgentType.critic,
                "description": "Agent1 description",
                "start_log_message": "Agent1 start log message",
                "finish_log_message": "Agent1 finish log message",
                "details": CriticDetails.Config.schema_extra["example"],
                "node": NodeModel.Config.schema_extra["example"],
            }
        }


class CreateUpdateAgentModel(BaseModel):
    """
    Create or update agent model.
    """

    name: str
    description: str
    agent_type: AgentType
    start_log_message: str
    finish_log_message: str
    details: CreateUpdateAgentDetails
    node: CreateNodeRequestModel
