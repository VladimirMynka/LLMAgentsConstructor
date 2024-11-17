from enum import Enum

from pydantic import BaseModel

from src.models.agent import AgentModel
from src.models.document_template import DocumentTemplateModel
from src.models.graph import GraphModel


class ContentType(str, Enum):
    AGENT = "agent"
    DOCUMENT_TEMPLATE = "document_template"


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
    content: AgentModel | DocumentTemplateModel

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
                    "content_type": ContentType.DOCUMENT_TEMPLATE,
                    "content": DocumentTemplateModel.Config.schema_extra["example"],
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
