from fastapi import APIRouter, FastAPI

from .controllers import *

app = FastAPI()

main_router = APIRouter("/api")

providers_router.include_router(models_router)

group_router.include_router(group_graphs_router)
group_router.include_router(group_providers_router)
group_router.include_router(group_prompts_router)
group_router.include_router(members_router)

graphs_router.include_router(nodes_router)
graphs_router.include_router(settings_router)
graphs_router.include_router(agents_router)

main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(group_router)
main_router.include_router(graphs_router)
main_router.include_router(providers_router)
main_router.include_router(prompts_router)

app.include_router(main_router)
