from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.document_template import (
    DocumentTemplateHasInstancesError,
    DocumentTemplateNotFoundError,
)
from src.db.errors.graph import GraphNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.document_template_service import DocumentTemplateService
from src.models.document_template import (
    CreateDocumentTemplateRequestModel,
    ExtendedDocumentTemplateModel,
    UpdateDocumentTemplateRequestModel,
)

router = APIRouter(prefix="/graphs/{graph_id}/document_templates")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except GraphNotFoundError:
            raise HTTPException(status_code=404, detail="Graph not found")
        except DocumentTemplateNotFoundError:
            raise HTTPException(status_code=404, detail="Document template not found")
        except DocumentTemplateHasInstancesError:
            raise HTTPException(
                status_code=403, detail="Document template has instances"
            )

    return wrapper


@router.post("/ai")
@map_errors
def create_document_template(
    graph_id: int,
    body: CreateDocumentTemplateRequestModel,
    token: str = Depends(get_token),
) -> list[ExtendedDocumentTemplateModel]:
    """
    Create AI agent.

    Args:
        graph_id: int - Graph id
        body: CreateUpdateAIAgentModel - Agent data
        token: str - Authentication token

    Returns:
        list[ExtendedDocumentTemplateModel] - List of document templates

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Agent not found"): If the agent not found
    """
    return DocumentTemplateService.create_document_template(graph_id, body, token)


@router.get("/")
@map_errors
def get_document_templates(
    graph_id: int,
    token: str = Depends(get_token),
) -> list[ExtendedDocumentTemplateModel]:
    """
    Get all document templates of graph.

    Args:
        graph_id: int - Graph id
        token: str - Authentication token

    Returns:
        list[ExtendedAgentModel] - List of agents

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
    """
    return DocumentTemplateService.get_document_templates(graph_id, token)


@router.get("/{document_template_id}")
@map_errors
def get_document_template(
    graph_id: int,
    document_template_id: int,
    token: str = Depends(get_token),
) -> ExtendedDocumentTemplateModel:
    """
    Get document template info.

    Args:
        graph_id: int - Graph id
        document_template_id: int - Document template id
        token: str - Authentication token

    Returns:
        ExtendedAgentModel - Agent

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Document template not found"): If the document template not found
    """
    return DocumentTemplateService.get_document_template(
        graph_id, document_template_id, token
    )


@router.delete("/{document_template_id}")
@map_errors
def delete_document_template(
    graph_id: int,
    document_template_id: int,
    token: str = Depends(get_token),
):
    """
    Delete document template.

    Args:
        graph_id: int - Graph id
        document_template_id: int - Document template id
        token: str - Authentication token

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(403, detail="Document template has instances"): If the document template has instances
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Document template not found"): If the document template not found
    """
    DocumentTemplateService.delete_document_template(
        graph_id, document_template_id, token
    )


@router.put("/{document_template_id}")
@map_errors
def update_document_template(
    graph_id: int,
    document_template_id: int,
    body: UpdateDocumentTemplateRequestModel,
    token: str = Depends(get_token),
):
    """
    Update document template.

    Args:
        graph_id: int - Graph id
        document_template_id: int - Document template id
        body: UpdateDocumentTemplateRequestModel - Document template data
        token: str - Authentication token

    Raises:
        HTTPException(401): If the authentication token is invalid
        HTTPException(404, detail="Graph not found"): If the user has no access to the graph or graph not found
        HTTPException(404, detail="Document template not found"): If the document template not found
    """
    DocumentTemplateService.update_document_template(
        graph_id, document_template_id, body, token
    )
