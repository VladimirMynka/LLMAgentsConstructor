from dataclasses import Field

from openai import BaseModel

from src.models.graph import GraphModel
from src.models.user import UserModel


class GroupModel(BaseModel):
    """
    Group model.
    """

    id: int = Field(..., description="Group id")
    name: str = Field(..., description="Group name")

    class Config:
        schema_extra = {"example": {"id": 1, "name": "TheBestGroup"}}


class GroupPermissionsModel(BaseModel):
    """
    Group permissions model.
    """

    owner: bool | None = Field(..., description="This user is owner of the group")
    change_members: bool | None = Field(
        ..., description="This user can edit another users permissions"
    )
    add_graphs: bool | None = Field(
        ..., description="This user can add graphs to the group"
    )
    run_graphs: bool | None = Field(
        ..., description="This user can run graphs in the group"
    )
    change_graphs_permissions: bool | None = Field(
        ..., description="This user can edit graphs permissions"
    )
    delete_graphs: bool | None = Field(
        ..., description="This user can delete graphs from the group"
    )

    class Config:
        schema_extra = {
            "example": {
                "owner": True,
                "add_users": True,
                "edit_users_permissions": True,
                "delete_users": True,
                "add_graphs": True,
                "edit_graphs_permissions": True,
                "delete_graphs": True,
            }
        }


class UserGroupModel(BaseModel):
    """
    User group model.
    """

    group_id: int = Field(..., description="Group id")
    group_name: str = Field(..., description="Group name")
    permissions: GroupPermissionsModel = Field(
        ..., description="User permissions in the group"
    )

    class Config:
        schema_extra = {
            "example": {
                "group_id": 1,
                "group_name": "Group name",
                "permissions": GroupPermissionsModel.Config.schema_extra["example"],
            }
        }


class MemberModel(BaseModel):
    """
    Member model.
    """

    user: UserModel = Field(..., description="User model")
    permissions: GroupPermissionsModel = Field(
        ..., description="User permissions in the group"
    )

    class Config:
        schema_extra = {
            "example": {
                "user": UserModel.Config.schema_extra["example"],
                "permissions": GroupPermissionsModel.Config.schema_extra["example"],
            }
        }


class GetGroupByIdRequestModel(BaseModel):
    """
    Get group by id request model.
    """

    id: int = Field(..., description="Group id")

    class Config:
        schema_extra = {"example": {"id": 1}}


class ExpandGroupModel(BaseModel):
    """
    Expand group model.
    """

    id: int = Field(..., description="Group id")
    name: str = Field(..., description="Group name")
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


class AddMemberRequestModel(BaseModel):
    """
    Add group member request model.
    """

    user_id: int = Field(..., description="user_id of the member")
    permissions: GroupPermissionsModel = Field(
        ..., description="User permissions in the group"
    )

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "permissions": GroupPermissionsModel.Config.schema_extra["example"],
            }
        }


class DeleteGroupResponseModel(BaseModel):
    """
    Delete group response model.
    """

    id: int = Field(..., description="Group id")

    class Config:
        schema_extra = {"example": {"id": 1}}
