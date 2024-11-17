from pydantic import BaseModel, Field

from src.db.entities.agent import AgentType
from src.models.agent_details import (
    AgentDetails,
    AIDetails,
    ChatDetails,
    CreateUpdateAgentDetails,
    CreateUpdateAIDetails,
    CreateUpdateChatDetails,
    CreateUpdateCriticDetails,
    CreateUpdateHardCodeDetails,
    CriticDetails,
    HardCodeDetails,
)
from src.models.node import CreateNodeRequestModel, NodeModel


class AgentModel(BaseModel):
    """
    Agent model.
    """

    id: int = Field(..., description="Agent id")
    name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    description: str = Field(..., description="Agent description")

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

    start_log_message: str = Field(..., description="Agent start log message")
    finish_log_message: str = Field(..., description="Agent finish log message")
    details: AgentDetails = Field(..., description="Agent details")
    node: NodeModel = Field(..., description="Node for agent")

    class Config:
        schema_extra = {
            "examples": [
                {
                    "id": 1,
                    "name": "Agent1",
                    "agent_type": AgentType.critic,
                    "description": "Agent1 description",
                    "start_log_message": "Agent1 start log message",
                    "finish_log_message": "Agent1 finish log message",
                    "details": CriticDetails.Config.schema_extra["example"],
                    "node": NodeModel.Config.schema_extra["example"],
                },
                {
                    "id": 2,
                    "name": "Agent2",
                    "agent_type": AgentType.ai,
                    "description": "Agent2 description",
                    "start_log_message": "Agent2 start log message",
                    "finish_log_message": "Agent2 finish log message",
                    "details": AIDetails.Config.schema_extra["example"],
                    "node": NodeModel.Config.schema_extra["example"],
                },
                {
                    "id": 3,
                    "name": "Agent3",
                    "agent_type": AgentType.hard_code,
                    "description": "Agent3 description",
                    "start_log_message": "Agent3 start log message",
                    "finish_log_message": "Agent3 finish log message",
                    "details": HardCodeDetails.Config.schema_extra["example"],
                    "node": NodeModel.Config.schema_extra["example"],
                },
                {
                    "id": 4,
                    "name": "Agent4",
                    "agent_type": AgentType.chat,
                    "description": "Agent4 description",
                    "start_log_message": "Agent4 start log message",
                    "finish_log_message": "Agent4 finish log message",
                    "details": ChatDetails.Config.schema_extra["example"],
                    "node": NodeModel.Config.schema_extra["example"],
                },
            ]
        }


class CreateUpdateAgentModel(BaseModel):
    """
    Create or update agent model.
    """

    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    agent_type: AgentType = Field(..., description="Agent type")
    start_log_message: str = Field(..., description="Agent start log message")
    finish_log_message: str = Field(..., description="Agent finish log message")
    details: CreateUpdateAgentDetails = Field(..., description="Agent details")
    node: CreateNodeRequestModel | None = Field(
        ..., description="Node for agent. Null for updating agent."
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Agent1",
                "description": "Agent1 description",
                "agent_type": AgentType.ai,
                "start_log_message": "Agent1 start log message",
                "finish_log_message": "Agent1 finish log message",
                "details": CreateUpdateAgentDetails.Config.schema_extra["example"],
                "node": CreateNodeRequestModel.Config.schema_extra["example"],
            }
        }


class CreateUpdateHardCodeAgentModel(CreateUpdateAgentModel):
    """
    Create or update hard-coded agent model.
    """

    details: CreateUpdateHardCodeDetails = Field(..., description="Agent details")

    class Config:
        schema_extra = {
            "example": {
                "name": "Agent1",
                "description": "Agent1 description",
                "agent_type": AgentType.hard_code,
                "start_log_message": "Agent1 start log message",
                "finish_log_message": "Agent1 finish log message",
                "details": CreateUpdateHardCodeDetails.Config.schema_extra["example"],
                "node": CreateNodeRequestModel.Config.schema_extra["example"],
            }
        }


class CreateUpdateChatAgentModel(CreateUpdateAgentModel):
    """
    Create or update chat agent model.
    """

    details: CreateUpdateChatDetails = Field(..., description="Agent details")

    class Config:
        schema_extra = {
            "example": {
                "name": "Agent1",
                "description": "Agent1 description",
                "agent_type": AgentType.chat,
                "start_log_message": "Agent1 start log message",
                "finish_log_message": "Agent1 finish log message",
                "details": CreateUpdateChatDetails.Config.schema_extra["example"],
                "node": CreateNodeRequestModel.Config.schema_extra["example"],
            }
        }


class CreateUpdateAIAgentModel(CreateUpdateAgentModel):
    """
    Create or update AI agent model.
    """

    details: CreateUpdateAIDetails = Field(..., description="Agent details")

    class Config:
        schema_extra = {
            "example": {
                "name": "Agent1",
                "description": "Agent1 description",
                "agent_type": AgentType.ai,
                "start_log_message": "Agent1 start log message",
                "finish_log_message": "Agent1 finish log message",
                "details": CreateUpdateAIDetails.Config.schema_extra["example"],
                "node": CreateNodeRequestModel.Config.schema_extra["example"],
            }
        }


class CreateUpdateCriticAgentModel(CreateUpdateAgentModel):
    """
    Create or update critic agent model.
    """

    details: CreateUpdateCriticDetails = Field(..., description="Agent details")

    class Config:
        schema_extra = {
            "example": {
                "name": "Agent1",
                "description": "Agent1 description",
                "agent_type": AgentType.critic,
                "start_log_message": "Agent1 start log message",
                "finish_log_message": "Agent1 finish log message",
                "details": CreateUpdateCriticDetails.Config.schema_extra["example"],
                "node": CreateNodeRequestModel.Config.schema_extra["example"],
            }
        }
