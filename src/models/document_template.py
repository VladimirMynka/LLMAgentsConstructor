from pydantic import BaseModel

from src.models.agent import AgentModel
from src.models.document import DocumentModel
from src.models.node import CreateNodeRequestModel, NodeModel


class DocumentTemplateModel(BaseModel):
    """
    Document template model.
    """

    id: int
    name: str
    description: str
    creator: AgentModel

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "SystemAnalystReport",
                "filename": "system_analyst_report.md",
                "description": "System analyst report with all the details",
                "creator": AgentModel.Config.schema_extra["example"],
            }
        }


class ExtendedDocumentTemplateModel(DocumentTemplateModel):
    """
    Extended document template model.
    """

    node: NodeModel
    instances: list[DocumentModel]

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "SystemAnalystReport",
                "filename": "system_analyst_report.md",
                "description": "System analyst report with all the details",
                "creator": AgentModel.Config.schema_extra["example"],
                "node": NodeModel.Config.schema_extra["example"],
                "instances": [DocumentModel.Config.schema_extra["example"]],
            }
        }


class CreateDocumentTemplateRequestModel(BaseModel):
    """
    Create document template request model.
    """

    name: str
    description: str
    creator_id: int
    node: CreateNodeRequestModel

    class Config:
        schema_extra = {
            "example": {
                "name": "HelloWorld",
                "description": "Write a hello world code",
                "filename": "hello_world.md",
                "creator_id": 1,
                "node": CreateNodeRequestModel.Config.schema_extra["example"],
            }
        }


class UpdateDocumentTemplateRequestModel(BaseModel):
    """
    Update document template request model.
    """

    name: str
    description: str
    creator_id: int

    class Config:
        schema_extra = {
            "example": {
                "name": "HelloWorld",
                "description": "Write a hello world code",
                "filename": "hello_world.md",
            }
        }
