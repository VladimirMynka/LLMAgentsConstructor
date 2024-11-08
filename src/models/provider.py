from pydantic import BaseModel

from src.models.group import GroupModel


class ProviderModel(BaseModel):
    """
    Provider model.
    """

    id: int
    name: str
    url: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "OpenAI",
                "url": "https://api.openai.com",
            }
        }


class ExpandProviderModel(ProviderModel):
    """
    Expand provider model.
    """

    groups: list[GroupModel]

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "OpenAI",
                "url": "https://api.openai.com",
                "groups": [GroupModel.Config.schema_extra["example"]],
            }
        }


class CreateProviderRequestModel(BaseModel):
    """
    Create provider request model.
    """

    name: str
    url: str

    class Config:
        schema_extra = {
            "example": {
                "name": "OpenAI",
                "url": "https://api.openai.com",
            }
        }


class UpdateProviderRequestModel(BaseModel):
    """
    Update provider request model.
    """

    name: str
    url: str

    class Config:
        schema_extra = {
            "example": {
                "name": "OpenAI",
                "url": "https://api.openai.com",
            }
        }


class AddProviderToGroupRequestModel(BaseModel):
    """
    Add provider to group request model.
    """

    provider_id: int

    class Config:
        schema_extra = {
            "example": {
                "provider_id": 1,
            }
        }
