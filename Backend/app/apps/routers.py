from fastapi.routing import APIRouter

from .token.endpoints import token_router
from .users.endpoints import user_router

api_router = APIRouter()
api_router.include_router(
		router=token_router,
		prefix="/token",
		include_in_schema=True,
		tags=["Token operations"],
		deprecated=False,
)

api_router.include_router(
		router=user_router,
		prefix="/accounts",
		tags=["Authentication"],
		include_in_schema=True,
)
