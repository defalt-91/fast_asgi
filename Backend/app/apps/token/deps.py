import dataclasses
import typing
import fastapi as fast
import jose
import pydantic
import sqlalchemy.orm.session as sql_session
import fastapi.security.oauth2 as f_oauth
import apps.users.models as u_models
import apps.scopes.schemas as s_schemas
import apps.token.schemas as t_schemas
import services.scopes as scope_service
import services.security_service as security_service
import apps.token.protocols as t_proto
from core.database.session import get_session
import services.errors as errors
from . import components
import apps.users.UserDAL as UserDAL
import events.emmiters as emitters


oauth2_refresh_token_reader = components.GetRefreshToken(cookie_name='refresh_token')
oauth2_refresh_token_writer = components.WriteRefreshTokenCookie(cookie_name="refresh_token")

AccessTokenClaimsFactory = t_schemas.AccessClaimsFactory()
RefreshTokenClaimsFactory = t_schemas.RefreshClaimsFactory()


async def add_user_scopes(user: u_models.User) -> typing.List[scope_service.ScopeTypes]:
	"""get user and add all user scopes in db to a list and return it"""
	if user.is_admin:
		return ["admin"]
	else:
		scope: s_schemas.ScopeOut
		# for scope in form_data.scopes:
		# 	if scope.lower() == 'me':
		# 		allowed_scopes.append('me')
		# 	if scope.lower() == 'posts':
		# 		allowed_scopes.append('posts')
		allowed_scopes = [scope.code for scope in user.scopes]
		return allowed_scopes


async def create_refresh_token(user: u_models.User, claims: t_schemas.JwtClaims) -> t_schemas.JwtClaims:
	try:
		claims.scopes = await add_user_scopes(user=user)
		claims.sub = user.username
		claims.token = await security_service.create_token(jwt_claims=claims)
	
	except (pydantic.ValidationError, jose.JWSError):
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="Not a valid refresh token, please login again",
		)
	return claims


async def create_access_token(
	sub: str,
	scopes: list,
	claims: t_schemas.JwtClaims
) -> t_schemas.JwtClaims:
	try:
		claims.sub = sub
		claims.scopes = scopes
		claims.token = await security_service.create_token(jwt_claims=claims)
	except (pydantic.ValidationError, jose.JWSError):
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="Not a valid refresh token, please login again",
		)
	return claims


async def access_token_from_refresh_token(
	refresh_token: oauth2_refresh_token_reader = fast.Depends(),
	claims: t_schemas.JwtClaims = fast.Depends(AccessTokenClaimsFactory)
) -> t_schemas.JwtClaims:
	try:
		payload = await security_service.decode_token(refresh_token)
		claims.sub = payload.get("sub", None)
		claims.scopes = payload.get("scopes", None)
		claims.token = await security_service.create_token(jwt_claims=claims)
	except (pydantic.ValidationError, jose.JWSError, jose.ExpiredSignatureError):
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="Not a valid refresh token, please login again",
		)
	
	return claims


# jwt_service = components.JWTService(jwt_verifier=verifier, jwt_creator=creator)
# Authorizer: t_proto.JWTAuthorizerProtocol = components.JWTAuthorizer(
# 	jwt_service=jwt_service, cookie_writer=oauth2_refresh_token_writer
# )

class LoginHandler:
	def __init__(self, cookie_writer, token_creator):
		self.cookie_writer = cookie_writer
		self.token_creator = token_creator
	
	async def __call__(
		self, *, response: fast.Response,
		form_data: f_oauth.OAuth2PasswordRequestForm = fast.Depends(),
		session: sql_session.Session = fast.Depends(get_session),
		refresh_token_jwt_claims: t_schemas.JwtClaims = fast.Depends(RefreshTokenClaimsFactory),
		access_token_jwt_claims: t_schemas.JwtClaims = fast.Depends(AccessTokenClaimsFactory),
	):
		user = UserDAL.user_dal.authenticate(
			username=form_data.username, raw_password=form_data.password, session=session
		)
		if not user:
			raise errors.incorrect_username_or_password()
		if not user.is_active:
			raise errors.inactive_user()
		refresh_token_jwt_claims.sub = user.username
		refresh_token_jwt_claims.scopes = [scope.code for scope in user.scopes]
		
		refresh_token_jwt_claims.token = self.token_creator(
			claims=refresh_token_jwt_claims,
			token_type="refresh_token"
		)
		access_token_jwt_claims.sub = user.username
		access_token_jwt_claims.scopes = refresh_token_jwt_claims.scopes
		access_token_jwt_claims.token = self.token_creator(claims=access_token_jwt_claims)
		self.cookie_writer(cookie_value=refresh_token_jwt_claims.token, response=response)
		emitters.emmit_refresh_token_creation(
			session=session, refresh_token_claims=refresh_token_jwt_claims, user_id=user.id
		)
		return access_token_jwt_claims


verifier = components.JWTVerifier()
creator = components.JWTCreator()
login_handler = LoginHandler(cookie_writer=oauth2_refresh_token_writer, token_creator=creator)
