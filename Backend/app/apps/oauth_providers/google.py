from fastapi import Request
from .oauth_registry import oauth
from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter


oauth_provider_router = APIRouter()


# redirect to Google account website
@oauth_provider_router.get("/login/google")
async def login_via_google(request: Request):
	redirect_uri = request.url_for("auth_via_google")
	return await oauth.google.authorize_redirect(request, redirect_uri)


# handle backed code and code_challenge and pkce
@oauth_provider_router.get('/auth/google')
async def auth_via_google(request: Request):
	try:
		token = await oauth.google.authorize_access_token(request)
	except OAuthError as error:
		return {"msg": error.error}
	user = await oauth.google.parse_id_token(request, token)
	return user


@oauth_provider_router.get("/logout")
async def logout(request: Request):
	request.session.pop("user", None)
	return {"msg": "You have been logout "}
