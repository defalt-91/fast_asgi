from authlib.integrations.starlette_client import OAuthError, OAuth
from starlette.config import Config


config = Config('.env')


"""for auto update token"""
oauth = OAuth(
	config=config,
	# update_token=update_token
)
oauth.register(
	name="google",
	server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
	client_kwargs={"scope": "openid email profile",'code_challenge_method': 'S256'}
)






# """ getting token from db"""
# def fetch_github_token(request):
#     token = OAuth2Token.find(
#         name='github',
#         user=request.user
#     )
#     return token.to_token()

oauth.register(
	name="github",
	# client_id="{{ your-github-client-id }}",
	# client_secret="{{ your-github-client-secret }}",
	access_token_url="https://github.com/login/oauth/access_token",
	access_token_params=None,
	authorize_url="https://github.com/login/oauth/authorize",
	authorize_params=None,
	api_base_url="https://api.github.com/",
	client_kwargs={
		"scope": "user:email",
		# for pcke enable
		# 'code_challenge_method': 'S256'
	},
	# """ for not query database for every request"""
	# fetch_token=fetch_github_token,
)
