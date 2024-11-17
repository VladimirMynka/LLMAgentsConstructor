from pydantic import BaseModel

from src.models.model import ExpandModelModel


class SettingsModel(BaseModel):
    """
    Settings model.
    """

    id: int
    model: ExpandModelModel
    temperature: float
    n: int
    frequency_penalty: float
    presence_penalty: float

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "model": ExpandModelModel.Config.schema_extra["example"],
                "temperature": 0.5,
                "n": 1,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }
        }


class CreateSettingsModel(BaseModel):
    """
    Create settings model.
    """

    model_id: int
    temperature: float
    n: int
    frequency_penalty: float
    presence_penalty: float

    class Config:
        schema_extra = {
            "example": {
                "model_id": 1,
                "temperature": 0.5,
                "n": 1,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            }
        }
