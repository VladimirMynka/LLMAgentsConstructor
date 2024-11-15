from typing import TypeAlias

from pydantic import BaseModel, field_validator

from src.db.entities.hard_code_agent import PredefinedType
from src.models.prompt import CreatePromptRequestModel, PromptModel
from src.models.settings import CreateSettingsModel, SettingsModel

AgentDetails: TypeAlias = BaseModel

CreateUpdateAgentDetails: TypeAlias = BaseModel


class AIDetails(AgentDetails):
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


class CreateUpdateAIDetails(CreateUpdateAgentDetails):
    """
    Create or update AI agent details.
    If settings_id is None, settings will be created.
    """

    prompt_id: int
    settings_id: int | None
    settings: CreateSettingsModel | None

    @field_validator("settings", "settings_id")
    def validate_settings(cls, settings_value, values):
        if settings_value is None and values.get("settings_id") is None:
            raise ValueError("Either settings or settings_id must be provided")
        return settings_value

    class Config:
        schema_extra = {
            "examples": [
                {
                    "prompt_id": 1,
                    "settings_id": None,
                    "settings": CreateSettingsModel.Config.schema_extra["example"],
                },
                {
                    "prompt_id": 1,
                    "settings_id": 1,
                    "settings": None,
                },
            ]
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


class CreateUpdateChatDetails(CreateUpdateAIDetails):
    """
    Create or update chat agent details.
    """

    stopwords: list[str]

    class Config:
        schema_extra = {
            "example": {
                "prompt_id": 1,
                "settings_id": 1,
                "settings": None,
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


class CreateUpdateCriticDetails(CreateUpdateAIDetails):
    """
    Create or update critic agent details.
    """

    criticized_id: int

    class Config:
        schema_extra = {
            "example": {
                "prompt_id": 1,
                "settings_id": 1,
                "settings": None,
                "criticized_id": 1,
            }
        }


class HardCodeDetails(AgentDetails):
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


class CreateUpdateHardCodeDetails(CreateUpdateAgentDetails):
    """
    Create or update hard-coded agent details.
    """

    predefined_type: PredefinedType

    class Config:
        schema_extra = {
            "example": {
                "predefined_type": PredefinedType.replace_text,
            }
        }
