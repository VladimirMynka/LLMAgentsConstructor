from pydantic import BaseModel

from src.models.group import GroupModel


class PromptModel(BaseModel):
    """
    Prompt model.
    """

    id: int
    name: str
    text: str

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "HelloWorld",
                "text": "Write a hello world code",
            }
        }


class ExpandPromptModel(PromptModel):
    """
    Expand prompt model.
    """

    groups: list[GroupModel]

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "HelloWorld",
                "text": "Write a hello world code",
                "groups": [GroupModel.Config.schema_extra["example"]],
            }
        }


class CreatePromptRequestModel(BaseModel):
    """
    Create prompt request model.
    """

    name: str
    text: str

    class Config:
        schema_extra = {
            "example": {
                "name": "HelloWorld",
                "text": "Write a hello world code",
            }
        }


class UpdatePromptRequestModel(BaseModel):
    """
    Update prompt request model.
    """

    name: str
    text: str

    class Config:
        schema_extra = {
            "example": {
                "name": "HelloWorld",
                "text": "Write a hello world code",
            }
        }


class AddPromptToGroupRequestModel(BaseModel):
    """
    Add prompt to group request model.
    """

    prompt_id: int

    class Config:
        schema_extra = {
            "example": {
                "prompt_id": 1,
            }
        }
