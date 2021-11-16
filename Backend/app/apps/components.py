import uuid
import attr
import sqlalchemy.orm
from starlette.responses import Response
from starlette.requests import Request
from starlette import status
from core.base_settings import get_settings
from typing import Literal
from fastapi import HTTPException, security, Depends, Security
from pydantic import ValidationError
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import sqlalchemy.orm.session as sql_session
import apps.users.models as u_models
import apps.token.schemas as t_schemas
from core.database.session import get_session
from events.emmiters import emmit_refresh_token_creation
from services import errors

import apps.token.protocols as t_proto
from services.errors import unauthorized_exception
from services.scopes import all_scopes
from apps.token.TokenDAL import token_dal
from apps.users.UserDAL import user_dal
import slowapi.middleware as sl_mid
import slowapi.util as sl_util


settings = get_settings()

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

limiter = sl_mid.Limiter(
	key_func=sl_util.get_remote_address,
	# headers_enabled=True,
	default_limits=["20/minute"],
	# storage_uri="redis://0.0.0.0:6379"
)

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl="Oauth/token",
	scopes=all_scopes,
)

@attr.s(hash=True, kw_only=True, slots=True, frozen=True, cache_hash=True)
class GetRefreshToken:
	cookie_name: str = attr.ib(default="refresh")
	
	async def __call__(self, request: Request) -> str:
		refresh_token: str = request.cookies.get(self.cookie_name)
		if not refresh_token:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="You are not authorize to get a new token, please to go to login page",
			)
		return refresh_token


oauth2_refresh_token_reader = GetRefreshToken(cookie_name="refresh_token")


@attr.s(hash=True, kw_only=True, slots=True, frozen=True, cache_hash=True)
class SetRefreshTokenCookie:
	cookie_name: str = attr.ib(default="refresh")
	expires = attr.ib(default=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60)
	
	async def __call__(self, cookie_value: str, response: Response) -> None:
		response.set_cookie(
			key=self.cookie_name,
			value=cookie_value,
			httponly=True,
			path="/",
			secure=False,
			samesite="strict",  # sending just to the site that wrote the cookie
			expires=self.expires,
			# domain="myawesomesite.io",  # subdomains are ignored , like api.myawesomesite.io ... just the domain is
			# needed
		)


headers = {"alg": settings.ALGORITHM, "typ": "JWT"}
refresh_cookie_writer = SetRefreshTokenCookie(cookie_name="refresh_token")


@attr.s(hash=True, slots=True, cache_hash=True, frozen=True, kw_only=True)
class JWTCreator:
	# headers: typing.Any = dataclasses.field(default_factory=lambda: )
	secret_key: str = attr.field(default=settings.SECRET_KEY)
	algorithm: str = attr.field(default=settings.ALGORITHM)
	
	async def __call__(
		self,
		claims: t_schemas.JwtClaims,
		token_type: Literal["access_token", "refresh_token"] = "access_token",
	) -> str:
		try:
			if token_type == "refresh_token":
				if claims.jti:
					claims.jti = str(claims.jti)
				else:
					raise ValueError("Refresh token claims needs jti")
			# delattr(claims,claims.token_type)
			return jwt.encode(
				claims=claims.dict(exclude_none=True, exclude={"token_type"}),
				key=self.secret_key,
				algorithm=self.algorithm,
				headers=headers,
			)
		# claims.jti = uuid.UUID(claims.jti)
		except (ValidationError, jwt.JWTError):
			raise HTTPException(
				status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="jwt didnt created"
			)


@attr.s(hash=True, slots=True, cache_hash=True, frozen=True, kw_only=True)
class JWTVerifier:
	secret_key: str = attr.ib(default=settings.SECRET_KEY)
	algorithm: jwt.ALGORITHMS = attr.ib(default=settings.ALGORITHM)
	issuer: str = attr.ib(default=settings.JWT_ISSUER)
	audience: str = attr.ib(default=settings.FRONTEND_ORIGIN)
	
	async def __call__(self, token: str) -> dict:
		try:
			return jwt.decode(
				token=token,
				key=self.secret_key,
				algorithms=[self.algorithm],
				issuer=self.issuer,
				audience=self.audience,
				options=Jwt_Options,
			)
		except jwt.ExpiredSignatureError:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Token has been expired, you need to log in again",
			)
		except jwt.JWTClaimsError:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Your token claims is not valid",
			)
		except jwt.JWTError:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="your credentials are not valid, signature is invalid",
			)


@attr.s(hash=True, slots=True, cache_hash=True, frozen=True, kw_only=True)
class JWTService:
	jwt_verifier: t_proto.JWTVerifierProtocol = attr.ib()
	jwt_creator: t_proto.JWTCreatorProtocol = attr.ib()


class UserFromForm:
	async def __call__(
		self,
		session: sqlalchemy.orm.Session = Depends(get_session),
		form_data: security.OAuth2PasswordRequestForm = Depends(),
	):
		user = user_dal.authenticate(
			session=session,
			username=form_data.username,
			raw_password=form_data.password,
		)
		if not user:
			raise errors.incorrect_username_or_password()
		if not user.is_active:
			raise errors.inactive_user()
		return user


user_from_form = UserFromForm()
oauth2_scheme = security.OAuth2PasswordBearer(
	tokenUrl="Oauth/token",
	scopes=all_scopes,
)


class GetCurrentUser:
	def __init__(self, jwt_verifier: JWTVerifier):
		self.jwt_verifier = jwt_verifier
	
	async def __call__(
		self,
		security_scopes: security.SecurityScopes,
		token=Depends(oauth2_scheme),
		session: sql_session.Session = Depends(get_session)
	):
		authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else f"Bearer"
		credentials_exception_need_detail = unauthorized_exception(authenticate_value)
		payload = await self.jwt_verifier(token=token)
		user_id: int = payload.get("sub")
		token_scopes_str: str = payload.get("scopes", None)
		user = session.get(u_models.User, ident=user_id)
		if not user:
			raise credentials_exception_need_detail("No user for this token")
		if "admin" in token_scopes_str:
			return user
		for scope in security_scopes.scopes:
			if scope not in token_scopes_str:
				raise credentials_exception_need_detail("Not enough permissions")
		return user


jwt_verifier_for_get_current_user = JWTVerifier()
currentUser = GetCurrentUser(jwt_verifier=jwt_verifier_for_get_current_user)


async def current_active_user(user: u_models.User = Security(currentUser, scopes=["me"])):
	if not user.is_active:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
	return user


async def current_active_superuser(user: u_models.User = Security(currentUser, scopes=["admin"])):
	if not user.is_admin:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="The user doesn't have enough privileges"
		)
	return user


class LoginHandler:
	def __init__(
		self,
		cookie_writer_callable: t_proto.CookieWriterProtocol,
		jwt_creator: t_proto.JWTCreatorProtocol,
	):
		self.cookie_writer = cookie_writer_callable
		self.token_creator = jwt_creator
	
	async def __call__(
		self,
		*,
		response: Response,
		session: sql_session.Session = Depends(get_session),
		user: u_models.User = Depends(user_from_form)
	):
		# user_scope_list = [scope.code for scope in user.scopes]
		user_scope_str = security.oauth2.SecurityScopes([scope.code for scope in user.scopes]).scope_str
		rt_claims: t_schemas.JwtClaims = t_schemas.JwtClaims.refresh_token(
			subject_id=str(user.id), scopes=user_scope_str
		)
		at_claims: t_schemas.JwtClaims = t_schemas.JwtClaims.access_token(
			subject_id=str(user.id), scopes=user_scope_str
		)
		refresh_token = await self.token_creator(claims=rt_claims, token_type="refresh_token")
		access_token = await self.token_creator(claims=at_claims, token_type="access_token")
		await self.cookie_writer(cookie_value=refresh_token, response=response)
		emmit_refresh_token_creation(
			session=session, refresh_token_claims=rt_claims, user_id=user.id, token=refresh_token
		)
		return access_token, at_claims


class AccessTokenFromRefreshToken:
	def __init__(self, jwt_service: t_proto.JWTServiceProtocol):
		self.jwt_service = jwt_service
	
	async def __call__(
		self,
		session: sql_session.Session = Depends(get_session),
		refresh_token=Depends(oauth2_refresh_token_reader)
	):
		payload = await self.jwt_service.jwt_verifier(refresh_token)
		db_token = token_dal.get_token(session=session, instance_jti=payload.get("jti"))
		if not db_token:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unacceptable auth credentials")
		if db_token.revoked:
			raise HTTPException(detail="this token is no longer valid", status_code=status.HTTP_403_FORBIDDEN)
		new_claims = t_schemas.JwtClaims.access_token(subject_id=payload.get("sub"), scopes=payload.get("scopes"))
		token = await self.jwt_service.jwt_creator(claims=new_claims, token_type="access_token")
		return token, new_claims.exp


class RevokeToken:
	async def __call__(
		self,
		token_jti: uuid.UUID,
		session: sql_session.Session = Depends(get_session),
		current_user: u_models.User = Depends(currentUser),
	):
		db_token = token_dal.get_token(session=session, instance_jti=token_jti)
		if not db_token:
			raise HTTPException(detail="Unacceptable token", status_code=status.HTTP_400_BAD_REQUEST)
		if db_token.revoked:
			raise HTTPException(detail="this token is already revoked", status_code=status.HTTP_208_ALREADY_REPORTED)
		if not current_user.is_admin and not (current_user.id == db_token.user_id):
			raise HTTPException(detail="you cant revoke this token", status_code=status.HTTP_403_FORBIDDEN)
		return token_dal.revoke_token(session=session, token=db_token)
