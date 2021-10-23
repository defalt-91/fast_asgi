from fastapi.routing import APIRouter

from apps.token.endpoints import token_router
from apps.posts.endpoint import post_router
from apps.users.endpoints import accounts

api_router = APIRouter()
api_router.include_router(
	router=token_router,
	prefix="/Oauth",
	include_in_schema=True,
	tags=["Authorization Server"],
	deprecated=False,
)

api_router.include_router(
	router=accounts,
	prefix="/users",
	tags=["Authentication Server"],
	include_in_schema=True,
)

api_router.include_router(
	router=post_router,
	prefix='/posts',
	include_in_schema=True,
	tags=['posts apis']
)
