import typing
import pydantic
import sqlalchemy.orm.session as sql_ses
import core.database.session as base_ses
import core.base_settings as b_settings
import fastapi.security as fast_security
import fastapi.param_functions as fast_params
import fastapi.exceptions as fast_exc
import slowapi.util as sl_util
import slowapi.middleware as sl_mid
import apps.token.schemas as t_schema
import apps.users.models as u_models
import apps.users.UserDAL as U_Dal
import jose.exceptions as j_exc
import jose.jwt as jwt
import services.errors as my_error
import services.scopes as sc_src
import starlette.requests as st_req
import starlette.status as st_status


settings = b_settings.get_settings()

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

""" load config for passlib hashing from .ini file """
# pwd_context_making_changes = pwd_context.load_path(path=Path(__name__).resolve().parent / "services/CryptContext.ini")


# limiter = Limiter(key_func=get_ipaddr, default_limits=["3/minute"])

limiter = sl_mid.Limiter(
	key_func=sl_util.get_remote_address,
	# headers_enabled=True,
	default_limits=["20/minute"],
	# storage_uri="redis://0.0.0.0:6379"
)


class OAuth2PasswordBearerCookieMode(fast_security.OAuth2PasswordBearer):
	async def __call__(self, request: st_req.Request) -> typing.Optional[str]:
		token: str = request.cookies.get("authorization")
		scheme, param = fast_security.oauth2.get_authorization_scheme_param(token)
		if not token or scheme.lower() != "bearer":
			if self.auto_error:
				raise fast_exc.HTTPException(
					status_code=st_status.HTTP_401_UNAUTHORIZED,
					detail="Not authenticated",
					headers={"WWW-Authenticate": "Bearer"},
				)
			else:
				return None
		return param


oauth2_scheme = fast_security.OAuth2PasswordBearer(
	tokenUrl="Oauth/token",
	scopes=sc_src.all_scopes,
)


def create_access_token(jwt_claims: t_schema.AccessTokenJwtClaims):
	headers = {"alg": settings.ALGORITHM, "typ": "JWT"}
	try:
		jwt_token = jwt.encode(
			claims=jwt_claims.dict(exclude_none=True),
			headers=headers,
			key=settings.SECRET_KEY,
			algorithm=settings.ALGORITHM,
		)
	except j_exc.JWTError:
		raise fast_exc.HTTPException(
			detail={"access_token": "error when encoding"},
			status_code=st_status.HTTP_406_NOT_ACCEPTABLE,
		)
	for_response = t_schema.AccessRefreshedForResponse(
		access_token=jwt_token,
		scopes=jwt_claims.scopes,
		exp=jwt_claims.exp,
		sub=jwt_claims.sub,
		iat=jwt_claims.iat,
		aud=jwt_claims.aud
	)
	return for_response


def create_refresh_token(token_claims: t_schema.RefreshTokenJwtClaims):
	headers = {"alg": settings.ALGORITHM, "typ": "JWT"}
	token_claims.jti = str(token_claims.jti)
	try:
		refresh_token = jwt.encode(
			claims=token_claims.dict(exclude_none=True),
			headers=headers,
			algorithm=settings.ALGORITHM,
			key=settings.SECRET_KEY
		)
	except(j_exc.JWTError, j_exc.JWTClaimsError):
		raise fast_exc.HTTPException(
			detail={"refresh_token": "error when encoding"},
			status_code=st_status.HTTP_406_NOT_ACCEPTABLE,
		)
	return refresh_token


async def get_current_user(
	security_scopes: fast_security.SecurityScopes,
	token: str = fast_params.Depends(oauth2_scheme),
	db: sql_ses.Session = fast_params.Depends(base_ses.get_session),
) -> u_models.User:
	"""Returns Current Authenticated User And Check For Scopes In Token"""
	if security_scopes.scopes:
		authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
	else:
		authenticate_value = f"Bearer"
	credentials_exception_need_detail = my_error.credentials_exception_need_detail(
		authenticate_value=authenticate_value
	)
	credentials_exception = credentials_exception_need_detail(
		details="Could not validate credentials"
	)
	try:
		payload = await decode_token(token)
		username: str = payload.get("sub")
		# if username is None:
		# 	raise credentials_exception
		token_scopes: typing.Optional[typing.List[typing.Any]] = payload.get("scopes", [])
		token_data = t_schema.TokenData(
			scopes=token_scopes, username=username, jti=payload.get("jti")
		)
	
	except pydantic.ValidationError:
		raise credentials_exception
	except j_exc.ExpiredSignatureError:
		raise credentials_exception_need_detail(
			details="signature has expired, you need to log in again"
		)
	except j_exc.JWTClaimsError:
		raise credentials_exception_need_detail(
			details="Your token claims is unacceptable"
		)
	except j_exc.JWTError:
		raise credentials_exception_need_detail(
			details="your credentials are not valid, signature is invalid"
		)
	
	user = U_Dal.user_dal.get_user_by_username(session=db, username=username)
	if user is None:
		raise credentials_exception_need_detail(details="No User Found !")
	# tokens = user.tokens
	# jti = token_data.jti
	for scope in security_scopes.scopes:
		# if 'admin' in token_data.scopes:
		# 	return user
		# elif scope not in token_data.scopes:
		# 	raise HTTPException(
		# 		status_code=status.HTTP_401_UNAUTHORIZED,
		# 		detail="Not enough scopes",
		# 		headers={"WWW-Authenticate": authenticate_value}
		# 	)
		if "admin" not in token_data.scopes and scope not in token_data.scopes:
			raise credentials_exception_need_detail(
				details="Not enough permission (scopes)"
			)
	return user


async def get_current_active_user(
	current_user: u_models.User = fast_params.Security(get_current_user, scopes=["me"])
) -> u_models.User:
	if not current_user.is_authenticated:
		raise my_error.inactive_user()
	return current_user


def get_current_active_superuser(
	current_user: u_models.User = fast_params.Security(get_current_active_user, scopes=["admin"]),
) -> u_models.User:
	return current_user


async def decode_token(token: str):
	return jwt.decode(
		token=token,
		key=settings.SECRET_KEY,
		algorithms=[settings.ALGORITHM],
		audience=settings.FRONTEND_ORIGIN,
		issuer=settings.JWT_ISSUER,
		# access_token=None,
		options=Jwt_Options,
	)
