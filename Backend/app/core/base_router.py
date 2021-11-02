import time
from typing import Callable

from fastapi.routing import APIRoute, APIRouter

from apps.oauth_providers.google import oauth_provider_router
from apps.token.endpoints import token_router
from apps.posts.endpoint import post_router
from apps.users.endpoints import accounts
from apps.scopes.endpoint import scope_api
from fastapi import Request, Response



class TimedRoute(APIRoute):
	def get_route_handler(self) -> Callable:
		original_route_handler = super().get_route_handler()
		
		async def custom_route_handler(request: Request) -> Response:
			before = time.time()
			response: Response = await original_route_handler(request)
			duration = time.time() - before
			response.headers["X-Response-Time"] = str(duration)
			print(f"route duration: {duration}")
			print(f"route response: {response}")
			print(f"route response headers: {response.headers}")
			return response
		
		return custom_route_handler


api_router = APIRouter(route_class=TimedRoute)
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
	router=post_router, prefix="/posts", include_in_schema=True, tags=["posts apis"]
)

api_router.include_router(
	scope_api,
	prefix="/scope",
	include_in_schema=True,
	tags=["Scope (Permission) managements"],
)
api_router.include_router(oauth_provider_router, tags=["Oauth2 providers"])

