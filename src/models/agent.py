from pydantic import BaseModel

from src.db.entities.agent import AgentType
from src.db.entities.hard_code_agent import PredefinedType
from src.models.prompt import PromptModel
from src.models.settings import SettingsModel


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


class AIDetails(BaseModel):
    """
    AI agent details.
    """

    prompt: PromptModel
    settings: SettingsModel

    class Config:
        schema_extra = {
            "example": {
                "prompt": PromptModel.Config.schema_extra["example"],
                "settings": SettingsModel.Config.schema_extra["example"],
            }
        }


class ChatDetails(AIDetails):
    """
    Chat agent details.
    """

    stopwords: list[str]

    class Config:
        schema_extra = {
            "example": {
                "prompt": PromptModel.Config.schema_extra["example"],
                "settings": SettingsModel.Config.schema_extra["example"],
                "stopwords": ["stopword1", "stopword2"],
            }
        }


class CriticDetails(AIDetails):
    """
    Critic agent details.
    """

    criticized_id: int

    class Config:
        schema_extra = {
            "example": {
                "prompt": PromptModel.Config.schema_extra["example"],
                "settings": SettingsModel.Config.schema_extra["example"],
                "criticized_id": 1,
            }
        }


class HardCodeDetails(BaseModel):
    """
    Hard-coded agent details.
    """

    predefined_type: PredefinedType

    class Config:
        schema_extra = {
            "example": {
                "predefined_type": PredefinedType.replace_text,
            }
        }


class ExtendedAgentModel(AgentModel):
    """
    Extended agent model.
    """

    details: AIDetails | ChatDetails | CriticDetails | HardCodeDetails

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Agent1",
                "agent_type": AgentType.critic,
                "description": "Agent1 description",
                "details": CriticDetails.Config.schema_extra["example"],
            }
        }
