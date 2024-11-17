from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.graph import GraphNotFoundError, UserIsNotGraphOwnerError
from src.db.errors.user import NotAuthorizedError
from src.db.services import GraphService
from src.models.graph import (
    CreateGraphRequestModel,
    ExpandGraphModel,
    GraphModel,
    UpdateGraphRequestModel,
)

router = APIRouter(prefix="/graphs")


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
        except UserIsNotGraphOwnerError:
            raise HTTPException(
                status_code=403, detail="User is not the owner of the graph"
            )
        except GraphNotFoundError:
            raise HTTPException(status_code=404, detail="Graph not found")

    return wrapper


@router.post("/")
@map_errors
async def create_graph(
    body: CreateGraphRequestModel,
    token: str = Depends(get_token),
) -> GraphModel:
    """
    Create a graph.

    Args:
        body: CreateGraphRequestModel - Graph data

    Returns:
        GraphModel - Graph data

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return GraphService.create_graph(body, token)


@router.get("/")
@map_errors
async def get_graphs(
    token: str = Depends(get_token),
) -> list[GraphModel]:
    """
    Get all graphs available for current user.

    Args:
        token: str - User authentication token

    Returns:
        list[GraphModel] - List of graphs

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return GraphService.get_graphs(token)


@router.get("/{graph_id}")
@map_errors
async def get_graph_by_id(
    graph_id: int,
    token: str = Depends(get_token),
) -> ExpandGraphModel:
    """
    Get graph by id.

    Args:
        graph_id: int - Graph id

    Returns:
        ExpandGraphModel - Graph info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the graph is not found or user has no access to it
    """
    return GraphService.get_graph_by_id(graph_id, token)


@router.put("/{graph_id}")
@map_errors
async def update_graph(
    graph_id: int,
    body: UpdateGraphRequestModel,
    token: str = Depends(get_token),
) -> GraphModel:
    """
    Update graph.

    Args:
        graph_id: int - Graph id
        body: UpdateGraphRequestModel - Graph data

    Returns:
        GraphModel - Graph data

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not the owner of the graph
        HTTPException(404): If the graph is not found or user has no access to it
    """
    return GraphService.update_graph(graph_id, body, token)


@router.delete("/{graph_id}")
@map_errors
async def delete_graph(
    graph_id: int,
    token: str = Depends(get_token),
) -> list[GraphModel]:
    """
    Delete graph.

    Args:
        graph_id: int - Graph id

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not the owner of the graph
        HTTPException(404): If the graph is not found or user has no access to it
    """
    return GraphService.delete_graph(graph_id, token)
