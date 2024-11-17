from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.graph import GraphNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.settings_service import SettingsService
from src.models.settings import SettingsModel

router = APIRouter(prefix="/{graph_id}/available_settings")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except GraphNotFoundError:
            raise HTTPException(status_code=404, detail="Graph not found")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")

    return wrapper


@router.get("/")
@map_errors
async def get_settings(
    graph_id: int,
    token: str = Depends(get_token),
) -> list[SettingsModel]:
    """
    Get all available settings in current context.

    Args:
        graph_id: int - Graph id
        token: str - User authentication token

    Returns:
        list[SettingsModel] - List of available settings

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the graph is not found or user has no access to it
    """
    return SettingsService.get_settings(graph_id, token)
