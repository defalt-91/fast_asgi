import dataclasses
import typing
import uuid

import fastapi
import typing_extensions as ty_ex
import fastapi.security.oauth2 as f_oauth
import fastapi as fast
import jose

import pydantic
import sqlalchemy.orm

import core.base_settings as b_settings

import apps.users.models as u_models
import apps.scopes.schemas as s_schemas
import apps.token.schemas as t_schemas
import services.scopes as scope_service
import services.security_service as security_service
from apps.users.UserDAL import user_dal
from core.database.session import get_session
import events.emmiters as emmiters
from services import errors
import jose.jwt as jwt


Jwt_Options = {
	"verify_signature": True,
	"verify_aud": True,
	"verify_iat": True,
	"verify_exp": True,
	"verify_nbf": False,
	"verify_iss": True,
	"verify_sub": True,
	"verify_jti": False,
	"verify_at_hash": False,
	"require_aud": True,
	"require_iat": True,
	"require_exp": True,
	"require_nbf": False,
	"require_iss": True,
	"require_sub": True,
	"require_jti": False,
	"require_at_hash": False,
	"leeway": 0,
}


class GetRefreshToken:
	async def __call__(self, request: fast.Request):
		refresh_token: str = request.cookies.get("refresh_token")
		if not refresh_token:
			raise fast.HTTPException(
				status_code=fast.status.HTTP_401_UNAUTHORIZED,
				detail="You are not authorize to get a new token, please to go to login page",
			)
		return refresh_token


oauth2_refresh_token = GetRefreshToken()
settings = b_settings.get_settings()

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
		scopes = await add_user_scopes(user=user)
		claims.scopes = scopes
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
	refresh_token: oauth2_refresh_token = fast.Depends(),
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


class CookieWriter(typing.Protocol):
	cookie_name: str
	""" cookie name must be past as class initializer parameter """
	
	def __call__(self, value: str, response: fastapi.Response) -> None:
		...
		""" this method writes the cookie"""


@dataclasses.dataclass(frozen=True)
class RefreshTokenCookieWriter:
	cookie_name: str
	
	def __call__(self, value: str, response: fast.Response):
		response.set_cookie(
			key=self.cookie_name, value=value, httponly=True, path="/", secure=False,
			samesite="strict",  # sending just to the site that wrote the cookie
			expires=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
			# domain="myawesomesite.io",  # subdomains are ignored , like api.myawesomesite.io ... just the domain is
			# needed
		)


class BaseJwtService(typing.Protocol):
	headers: dict
	
	def create_jwt(self, claims: t_schemas.JwtClaims, user: u_models.User, jti: bool) -> t_schemas.JwtClaims:
		""" for creating jwt tokens """
	
	def verify_jwt(self, token: str) -> dict:
		""" for verifying signature of jwt """


class JWTService:
	def __init__(self):
		self.headers = {"alg": settings.ALGORITHM, "typ": "JWT"}
		self.secret_key = settings.SECRET_KEY
		self.algorithm = settings.ALGORITHM
		self.issuer = settings.ISSUER
		self.audience = settings.FRONTEND_ORIGIN
		self.options = Jwt_Options
	
	def create_jwt(self, claims: t_schemas.JwtClaims, jti: bool = False):
		try:
			if jti:
				claims.jti = str(claims.jti)
			claims.token = jwt.encode(
				claims=claims.dict(exclude_none=True), key=self.secret_key, algorithm=self.algorithm,
				headers=self.headers
			)
			claims.jti = uuid.UUID(claims.jti)
			return claims
		except(pydantic.ValidationError, jwt.JWTError):
			raise fast.HTTPException(status_code=fast.status.HTTP_403_FORBIDDEN, detail="jwt didnt created")
	
	def verify_jwt(self, token):
		try:
			token = jwt.decode(
				token=token, key=self.secret_key, algorithms=[self.algorithm], issuer=self.issuer,
				audience=self.audience, options=self.options
			)
			return token
		except jwt.ExpiredSignatureError:
			raise fast.HTTPException(
				status_code=fast.status.HTTP_403_FORBIDDEN,
				detail="signature has expired, you need to log in again"
			)
		except jwt.JWTClaimsError:
			raise fast.HTTPException(
				status_code=fast.status.HTTP_403_FORBIDDEN,
				detail="Your token claims is unacceptable"
			)
		except jwt.JWTError:
			raise fast.HTTPException(
				status_code=fast.status.HTTP_403_FORBIDDEN,
				detail="your credentials are not valid, signature is invalid"
			)


class TokenCreator:
	def __init__(self, cookie_writer: CookieWriter,
		# jwt_service: BaseJwtService
	):
		self.cookie_writer = cookie_writer
		# self.jwt_service = jwt_service
	
	async def __call__(
		self,
		response: fastapi.Response,
		session: sqlalchemy.orm.Session = fast.Depends(get_session),
		form_data: f_oauth.OAuth2PasswordRequestForm = fast.Depends(),
		refresh_token_claims: t_schemas.JwtClaims = fast.Depends(RefreshTokenClaimsFactory),
	):
		user = user_dal.authenticate(session=session, username=form_data.username, raw_password=form_data.password)
		if not user:
			raise errors.incorrect_username_or_password()
		if not user.is_active:
			raise errors.inactive_user()
		
		claims_with_refresh_token = await create_refresh_token(claims=refresh_token_claims, user=user)
		
		emmiters.emmit_refresh_token_creation(
			session=session, user_id=user.id,
			refresh_token_claims=claims_with_refresh_token
		)
		self.cookie_writer(value=claims_with_refresh_token.token, response=response)
		return claims_with_refresh_token


RefreshTokenCookieHandler = RefreshTokenCookieWriter(cookie_name='refresh_token')
RefreshTokenHandler = TokenCreator(cookie_writer=RefreshTokenCookieHandler)
