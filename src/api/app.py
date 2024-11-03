from fastapi import APIRouter, FastAPI

from .controllers import user_router

app = FastAPI()

main_router = APIRouter("/api")

main_router.include_router(user_router)

app.include_router(main_router)
