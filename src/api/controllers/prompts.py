from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.prompt import PromptNotFoundError, UserIsNotPromptOwnerError
from src.db.errors.user import NotAuthorizedError
from src.db.services import PromptService
from src.models.prompt import (
    CreatePromptRequestModel,
    ExpandPromptModel,
    PromptModel,
    UpdatePromptRequestModel,
)

router = APIRouter(prefix="/prompts")


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
        except UserIsNotPromptOwnerError:
            raise HTTPException(
                status_code=403, detail="User is not the owner of the prompt"
            )
        except PromptNotFoundError:
            raise HTTPException(status_code=404, detail="Prompt not found")

    return wrapper


@router.post("/")
@map_errors
async def create_prompt(
    body: CreatePromptRequestModel,
    token: str = Depends(get_token),
) -> PromptModel:
    """
    Create a prompt.

    Args:
        body: CreatePromptRequestModel - Prompt data

    Returns:
        PromptModel - Prompt data

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return PromptService.create_prompt(body, token)


@router.get("/")
@map_errors
async def get_prompts(
    token: str = Depends(get_token),
) -> list[PromptModel]:
    """
    Get all prompts available for current user.

    Args:
        token: str - User authentication token

    Returns:
        list[PromptModel] - List of prompts

    Raises:
        HTTPException(401): If the user is not authorized
    """
    return PromptService.get_prompts(token)


@router.get("/{prompt_id}")
@map_errors
async def get_prompt_by_id(
    prompt_id: int,
    token: str = Depends(get_token),
) -> ExpandPromptModel:
    """
    Get prompt by id.

    Args:
        prompt_id: int - Prompt id

    Returns:
        ExpandPromptModel - Prompt info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the prompt is not found or user has no access to it
    """
    return PromptService.get_prompt_by_id(prompt_id, token)


@router.put("/{prompt_id}")
@map_errors
async def update_prompt(
    prompt_id: int,
    body: UpdatePromptRequestModel,
    token: str = Depends(get_token),
) -> PromptModel:
    """
    Update prompt.

    Args:
        prompt_id: int - Prompt id
        body: UpdatePromptRequestModel - Prompt data

    Returns:
        PromptModel - Prompt data

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not the owner of the prompt
        HTTPException(404): If the prompt is not found or user has no access to it
    """
    return PromptService.update_prompt(prompt_id, body, token)


@router.delete("/{prompt_id}")
@map_errors
async def delete_prompt(
    prompt_id: int,
    token: str = Depends(get_token),
) -> list[PromptModel]:
    """
    Delete prompt.

    Args:
        prompt_id: int - Prompt id

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(403): If the user is not the owner of the prompt
        HTTPException(404): If the prompt is not found or user has no access to it
    """
    return PromptService.delete_prompt(prompt_id, token)
