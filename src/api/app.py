from fastapi import APIRouter, FastAPI

from .controllers import *

app = FastAPI()

main_router = APIRouter("/api")

group_router.include_router(group_providers_router)
group_router.include_router(members_router)

main_router.include_router(user_router)
main_router.include_router(group_router)
main_router.include_router(providers_router)

app.include_router(main_router)
