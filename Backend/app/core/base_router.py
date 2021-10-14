from fastapi.routing import APIRouter

from apps.token.endpoints import token_router
from apps.users.endpoints import accounts

api_router = APIRouter()
api_router.include_router(
		router=token_router,
		prefix="/Oauth",
		include_in_schema=True,
		tags=["Token operations"],
		deprecated=False,
)

api_router.include_router(
		router=accounts,
		prefix="/accounts",
		tags=["Authentication"],
		include_in_schema=True,
)
