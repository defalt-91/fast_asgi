from authlib.integrations.starlette_client import OAuthError, OAuth
from fastapi import Request
from .oauth_registry import oauth
from .google import oauth_provider_router


@oauth_provider_router.route("/login/github")
async def login_via_github(request: Request):
	# absolute url for callback
	# we will define it below
	redirect_uri = request.url_for("auth_via_github")
	return await oauth.github.authorize_redirect(request, redirect_uri)


# obtain a token which contains access_token and id_token
# we just need to parse it to get the login user's information
@oauth_provider_router.get("/auth/github", name="auth")
async def auth_via_github(request: Request):
	try:
		token = await oauth.github.authorize_access_token(request)
	except OAuthError as error:
		return {"msg": error.error}
	# resp = oauth.github.get('user', token=token)
	# resp.raise_for_status()
	# profile = resp.json()
	user = await oauth.github.parse_id_token(request, token)
	
	if user:
		request.session["user"] = dict(user)
	return dict(user)




""" re authenticating if request.user"""
# def get_github_repositories(request):
#     token = OAuth2Token.find(
#         name='github',
#         user=request.user
#     )
#     user = oauth.github.userinfo(request)
#     # API URL: https://api.github.com/user/repos
#     resp = oauth.github.get('user/repos', token=token.to_token())

#   works when fetch_token function  is in  register
#     resp = oauth.github.get('user/repos', request=request)
#     resp.raise_for_status()
#     return resp.json()
