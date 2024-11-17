from dataclasses import Field

from pydantic import BaseModel

from src.models.graph import GraphModel
from src.models.member import MemberModel
from src.models.user import UserModel


class GroupModel(BaseModel):
    """
    Group model.
    """

    id: int = Field(..., description="Group id")
    name: str = Field(..., description="Group name")

    class Config:
        schema_extra = {"example": {"id": 1, "name": "TheBestGroup"}}


class ExpandGroupModel(GroupModel):
    """
    Expand group model.
    """

    owner: UserModel = Field(..., description="Group owner")
    members: list[MemberModel] = Field(..., description="Group members")
    graphs: list[GraphModel] = Field(..., description="Group graphs")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "TheBestGroup",
                "owner": UserModel.Config.schema_extra["example"],
                "members": [MemberModel.Config.schema_extra["example"]],
                "graphs": [GraphModel.Config.schema_extra["example"]],
            }
        }


class CreateGroupRequestModel(BaseModel):
    """
    Create group request model.
    """

    name: str = Field(..., description="Group name")
    members: list[int] = Field(..., description="user_id of the members")

    class Config:
        schema_extra = {"example": {"name": "TheBestGroup", "members": [1, 2, 3]}}


class UpdateGroupRequestModel(BaseModel):
    """
    Update group request model.
    """

    name: str | None = Field(..., description="Group name")

    class Config:
        schema_extra = {"example": {"name": "TheBestGroup"}}


class DeleteGroupResponseModel(BaseModel):
    """
    Delete group response model.
    """

    id: int = Field(..., description="Group id")

    class Config:
        schema_extra = {"example": {"id": 1}}
