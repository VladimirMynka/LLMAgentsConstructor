from .agents import router as agents_router
from .auth import router as auth_router
from .document_templates import router as document_templates_router
from .graphs import router as graphs_router
from .group_graphs import router as group_graphs_router
from .group_prompts import router as group_prompts_router
from .group_providers import router as group_providers_router
from .groups import router as group_router
from .members import router as members_router
from .models import router as models_router
from .nodes import router as nodes_router
from .prompts import router as prompts_router
from .providers import router as providers_router
from .settings import router as settings_router
from .users import router as user_router

__all__ = [
    "agents_router",
    "auth_router",
    "document_templates_router",
    "group_router",
    "group_providers_router",
    "group_prompts_router",
    "group_graphs_router",
    "members_router",
    "providers_router",
    "user_router",
    "prompts_router",
    "graphs_router",
    "models_router",
    "nodes_router",
    "settings_router",
]
