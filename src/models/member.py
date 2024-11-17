from dataclasses import Field

from pydantic import BaseModel

from src.models.user import UserModel


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
                "change_members": True,
                "add_graphs": True,
                "run_graphs": True,
                "change_graphs_permissions": True,
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
