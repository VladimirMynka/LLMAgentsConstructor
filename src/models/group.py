from dataclasses import Field

from openai import BaseModel


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
    add_users: bool | None = Field(
        ..., description="This user can add users to the group"
    )
    edit_users_permissions: bool | None = Field(
        ..., description="This user can edit another users permissions"
    )
    delete_users: bool | None = Field(
        ..., description="This user can delete users from the group"
    )
    add_graphs: bool | None = Field(
        ..., description="This user can add graphs to the group"
    )
    edit_graphs_permissions: bool | None = Field(
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
