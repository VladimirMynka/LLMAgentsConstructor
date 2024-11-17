from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.group import GroupNotFoundError, UserNotInGroupError
from src.db.errors.prompt import PromptAlreadyInGroupError, PromptNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.group_prompt_service import GroupPromptService
from src.models.prompt import AddPromptToGroupRequestModel, PromptModel

router = APIRouter(prefix="/{group_id}/prompts")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PromptAlreadyInGroupError:
            raise HTTPException(status_code=400, detail="Prompt already in the group")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except UserNotInGroupError:
            raise HTTPException(status_code=404, detail="Group not found")
        except GroupNotFoundError:
            raise HTTPException(status_code=404, detail="Group not found")
        except PromptNotFoundError:
            raise HTTPException(status_code=404, detail="Prompt not found")

    return wrapper


@router.post("/")
@map_errors
async def add_prompt_to_group(
    group_id: int,
    body: AddPromptToGroupRequestModel,
    token: str = Depends(get_token),
) -> list[PromptModel]:
    """
    Add prompt to group.

    Args:
        group_id: int - Group id
        body: AddPromptToGroupRequestModel - Add prompt to group request model

    Returns:
        list[PromptModel] - List of prompts

    Raises:
        HTTPException(400): If the prompt is already in the group
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
        HTTPException(404): If the prompt is not found
    """
    return GroupPromptService.add_group_prompt(body, group_id, token)


@router.get("/")
@map_errors
async def get_group_prompts(
    group_id: int,
    token: str = Depends(get_token),
) -> list[PromptModel]:
    """
    Get group prompts.

    Args:
        group_id: int - Group id

    Returns:
        list[PromptModel] - List of prompts

    Raises:
        HTTPException(401): If the requester is not authorized
        HTTPException(403): If the requester is not in the group
        HTTPException(404): If the group is not found
    """
    return GroupPromptService.get_group_prompts(group_id, token)
