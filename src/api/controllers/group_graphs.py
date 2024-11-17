from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.graph import GraphAlreadyInGroupError, GraphNotFoundError
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.user import NotAuthorizedError
from src.db.services.group_graph_service import GroupGraphService
from src.models.graph import AddGraphToGroupRequestModel, GraphModel

router = APIRouter(prefix="/{group_id}/graphs")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GraphAlreadyInGroupError:
            raise HTTPException(status_code=400, detail="Graph already in the group")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except UserNotInGroupError:
            raise HTTPException(status_code=404, detail="Group not found")
        except GroupNotFoundError:
            raise HTTPException(status_code=404, detail="Group not found")
        except GraphNotFoundError:
            raise HTTPException(status_code=404, detail="Graph not found")

    return wrapper


@router.post("/")
@map_errors
async def add_graph_to_group(
    group_id: int,
    body: AddGraphToGroupRequestModel,
    token: str = Depends(get_token),
) -> list[GraphModel]:
    """
    Add graph to group.

    Args:
        group_id: int - Group id
        body: AddGraphToGroupRequestModel - Add graph to group request model

    Returns:
        list[GraphModel] - List of graphs

    Raises:
        HTTPException(400): If the graph is already in the group
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
        HTTPException(404): If the graph is not found
    """
    return GroupGraphService.add_group_graph(body, group_id, token)


@router.get("/")
@map_errors
async def get_group_graphs(
    group_id: int,
    token: str = Depends(get_token),
) -> list[GraphModel]:
    """
    Get group graphs.

    Args:
        group_id: int - Group id

    Returns:
        list[GraphModel] - List of graphs

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
    """
    return GroupGraphService.get_group_graphs(group_id, token)
