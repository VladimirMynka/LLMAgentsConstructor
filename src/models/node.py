from enum import Enum
from typing import Literal

from pydantic import BaseModel

from src.models.agent import AgentModel
from src.models.document import DocumentModel
from src.models.graph import GraphModel


class ContentType(str, Enum):
    AGENT = "agent"
    DOCUMENT = "document"


class NodeModel(BaseModel):
    """
    Node model.
    """

    id: int
    x: int
    y: int
    content_type: ContentType

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "x": 100,
                "y": 100,
                "content_type": ContentType.AGENT,
            }
        }


class ExtendedNodeModel(NodeModel):
    """
    Extended node model.
    """

    graph: GraphModel
    content: AgentModel | DocumentModel

    class Config:
        schema_extra = {
            "examples": [
                {
                    "id": 1,
                    "x": 100,
                    "y": 100,
                    "graph": GraphModel.Config.schema_extra["example"],
                    "content_type": ContentType.AGENT,
                    "content": AgentModel.Config.schema_extra["example"],
                },
                {
                    "id": 2,
                    "x": 200,
                    "y": 200,
                    "graph": GraphModel.Config.schema_extra["example"],
                    "content_type": ContentType.DOCUMENT,
                    "content": DocumentModel.Config.schema_extra["example"],
                },
            ]
        }


class UpdateNodeRequestModel(BaseModel):
    """
    Update node request model.
    """

    id: int
    x: int
    y: int

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "x": 100,
                "y": 100,
            }
        }


class CreateNodeRequestModel(BaseModel):
    """
    Create node request model.
    """

    x: int
    y: int

    class Config:
        schema_extra = {
            "example": {
                "x": 100,
                "y": 100,
            }
        }
