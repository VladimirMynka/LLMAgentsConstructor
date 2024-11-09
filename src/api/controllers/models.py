from functools import wraps

from fastapi import APIRouter, Depends, HTTPException

from src.api.controllers.users import get_token
from src.db.errors.model import ModelAlreadyExistsError, ModelNotFoundError
from src.db.errors.provider import ProviderNotFoundError
from src.db.errors.user import NotAuthorizedError
from src.db.services.model_service import ModelService
from src.models.model import (
    CreateModelRequestModel,
    ModelModel,
    UpdateModelRequestModel,
)
from src.models.provider import ExpandProviderModel

router = APIRouter(prefix="/{provider_id}/models")


def map_errors(func):
    """
    Map service errors to HTTP exceptions.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ModelNotFoundError:
            raise HTTPException(status_code=404, detail="Model not found")
        except ProviderNotFoundError:
            raise HTTPException(status_code=404, detail="Provider not found")
        except NotAuthorizedError:
            raise HTTPException(status_code=401, detail="Unauthorized")
        except ModelAlreadyExistsError:
            raise HTTPException(status_code=400, detail="Model already exists")

    return wrapper


@router.post("/")
@map_errors
async def create_model(
    provider_id: int,
    body: CreateModelRequestModel,
    token: str = Depends(get_token),
) -> list[ModelModel]:
    """
    Create a model.

    Args:
        provider_id: int - Provider id
        body: CreateModelRequestModel - Model data

    Returns:
        ModelModel - Model data

    Raises:
        HTTPException(400): If the model already exists
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ModelService.create_model(provider_id, body, token)


@router.get("/")
@map_errors
async def get_models(
    provider_id: int,
    token: str = Depends(get_token),
) -> list[ModelModel]:
    """
    Get all models of provider.

    Args:
        provider_id: int - Provider id
        token: str - User authentication token

    Returns:
        list[ModelModel] - List of models

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404): If the provider is not found or user has no access to it
    """
    return ModelService.get_models(provider_id, token)


@router.get("/{model_id}")
@map_errors
async def get_model_by_id(
    provider_id: int,
    model_id: int,
    token: str = Depends(get_token),
) -> ExpandProviderModel:
    """
    Get model by id.

    Args:
        provider_id: int - Provider id
        model_id: int - Model id

    Returns:
        ExpandModelModel - Model info

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404, detail="Provider not found"): If the provider is not found or user has no access to it
        HTTPException(404, detail="Model not found"): If the model is not found
    """
    return ModelService.get_model_by_id(provider_id, model_id, token)


@router.put("/{model_id}")
@map_errors
async def update_model(
    provider_id: int,
    model_id: int,
    body: UpdateModelRequestModel,
    token: str = Depends(get_token),
) -> list[ModelModel]:
    """
    Update model.

    Args:
        provider_id: int - Provider id
        model_id: int - Model id
        body: UpdateModelRequestModel - Model data

    Returns:
        list[ModelModel] - List of models

    Raises:
        HTTPException(400): If the model already exists
        HTTPException(401): If the user is not authorized
        HTTPException(404, detail="Provider not found"): If the provider is not found or user has no access to it
        HTTPException(404, detail="Model not found"): If the model is not found
    """
    return ModelService.update_model(provider_id, model_id, body, token)


@router.delete("/{model_id}")
@map_errors
async def delete_model(
    provider_id: int,
    model_id: int,
    token: str = Depends(get_token),
) -> list[ModelModel]:
    """
    Delete model.

    Args:
        provider_id: int - Provider id
        model_id: int - Model id

    Returns:
        list[ModelModel] - List of models

    Raises:
        HTTPException(401): If the user is not authorized
        HTTPException(404, detail="Provider not found"): If the provider is not found or user has no access to it
        HTTPException(404, detail="Model not found"): If the model is not found
    """
    return ModelService.delete_model(provider_id, model_id, token)
