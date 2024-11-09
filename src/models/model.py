from pydantic import BaseModel

from src.models.provider import ProviderModel


class ModelModel(BaseModel):
    """
    Model model.
    """

    id: int
    name: str
    owner: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "gpt-4o",
                "owner": "openai",
            }
        }


class ExpandModelModel(ModelModel):
    """
    Expand model model.
    """

    provider: ProviderModel

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "gpt-4o",
                "owner": "openai",
                "provider": ProviderModel.Config.schema_extra["example"],
            }
        }


class CreateModelRequestModel(BaseModel):
    """
    Create model request model.
    """

    name: str
    owner: str

    class Config:
        schema_extra = {
            "example": {
                "name": "gpt-4o",
                "owner": "openai",
            }
        }


class UpdateModelRequestModel(BaseModel):
    """
    Update model request model.
    """

    name: str
    owner: str

    class Config:
        schema_extra = {
            "example": {
                "name": "gpt-4o",
                "owner": "openai",
            }
        }
