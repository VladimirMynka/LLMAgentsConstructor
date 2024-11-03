from dataclasses import Field

from openai import BaseModel


class GraphModel(BaseModel):
    """
    Graph model.
    """

    id: int = Field(..., description="Graph id")
    name: str = Field(..., description="Graph name")

    class Config:
        schema_extra = {"example": {"id": 1, "name": "TheBestGraph"}}
