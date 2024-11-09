from pydantic import BaseModel


class CreateProviderTokenRequestModel(BaseModel):
    token: str
