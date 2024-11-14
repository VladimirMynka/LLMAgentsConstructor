from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.graph import GraphNotFoundError
from src.db.errors.node import NodeNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.node_service import NodeService
from src.models.node import NodeModel, UpdateNodeRequestModel

router = APIRouter(prefix="/{graph_id}/nodes")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NodeNotFoundError:
            raise HTTPException(status_code=404, detail="Node not found")
        except GraphNotFoundError:
            raise HTTPException(status_code=404, detail="Graph not found")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")

    return wrapper


@router.get("/")
@map_errors
async def get_nodes(
    graph_id: int,
    token: str = Depends(get_token),
) -> list[NodeModel]:
    """
    Get all nodes of graph.

    Args:
        graph_id: int - Graph id
        token: str - User authentication token

    Returns:
        list[NodeModel] - List of nodes

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the graph is not found or user has no access to it
    """
    return NodeService.get_nodes(graph_id, token)


@router.get("/{node_id}")
@map_errors
async def get_node_by_id(
    graph_id: int,
    node_id: int,
    token: str = Depends(get_token),
) -> NodeModel:
    """
    Get node by id.

    Args:
        graph_id: int - Graph id
        node_id: int - Node id

    Returns:
        NodeModel - Node info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404, detail="Graph not found"): If the graph is not found or user has no access to it
        HTTPException(404, detail="Node not found"): If the node is not found
    """
    return NodeService.get_node_by_id(graph_id, node_id, token)


@router.put("/{node_id}")
@map_errors
async def move_node(
    graph_id: int,
    node_id: int,
    body: UpdateNodeRequestModel,
    token: str = Depends(get_token),
) -> list[NodeModel]:
    """
    Move node.

    Args:
        graph_id: int - Graph id
        node_id: int - Node id
        body: UpdateNodeRequestModel - Node data

    Returns:
        list[NodeModel] - List of nodes

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404, detail="Graph not found"): If the graph is not found or user has no access to it
        HTTPException(404, detail="Node not found"): If the node is not found
    """
    return NodeService.move_node(graph_id, node_id, body, token)
