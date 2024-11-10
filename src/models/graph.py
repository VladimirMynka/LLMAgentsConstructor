from dataclasses import Field

from pydantic import BaseModel

from src.models.group import GroupModel
from src.models.node import ExtendedNodeModel


class GraphModel(BaseModel):
    """
    Graph model.
    """

    id: int = Field(..., description="Graph id")
    name: str = Field(..., description="Graph name")
    description: str = Field(..., description="Graph description")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "TheBestGraph",
                "description": "The best graph",
            }
        }


class ExpandGraphModel(GraphModel):
    """
    Expand graph model.
    """

    groups: list[GroupModel]
    nodes: list[ExtendedNodeModel]

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "TheBestGraph",
                "description": "The best graph",
                "groups": [GroupModel.Config.schema_extra["example"]],
                "nodes": [ExtendedNodeModel.Config.schema_extra["example"]],
            }
        }


class CreateGraphRequestModel(BaseModel):
    """
    Create graph request model.
    """

    name: str
    description: str

    class Config:
        schema_extra = {
            "example": {
                "name": "TheBestGraph",
                "description": "The best graph",
            }
        }


class UpdateGraphRequestModel(BaseModel):
    """
    Update graph request model.
    """

    name: str
    description: str

    class Config:
        schema_extra = {
            "example": {
                "name": "TheBestGraph",
                "description": "The best graph",
            }
        }


class AddGraphToGroupRequestModel(BaseModel):
    """
    Add graph to group request model.
    """

    graph_id: int

    class Config:
        schema_extra = {
            "example": {
                "graph_id": 1,
            }
        }
