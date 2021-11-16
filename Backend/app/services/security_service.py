# import pydantic
# import sqlalchemy.orm.session as sql_ses
# import core.database.session as base_ses
# import core.base_settings as b_settings
# import fastapi.security as fast_security
# import fastapi.param_functions as fast_params
# import slowapi.util as sl_util
# import slowapi.middleware as sl_mid
# import apps.users.models as u_models
# import apps.users.UserDAL as U_Dal
# import jose.exceptions as j_exc
# import jose.jwt as jwt
# import services.errors as my_error
# import services.scopes as sc_src
#
#
# settings = b_settings.get_settings()
#
# Jwt_Options = {
# 	"verify_signature": True,
# 	"verify_aud": True,
# 	"verify_iat": True,
# 	"verify_exp": True,
# 	"verify_nbf": False,
# 	"verify_iss": True,
# 	"verify_sub": True,
# 	"verify_jti": False,
# 	"verify_at_hash": False,
# 	"require_aud": True,
# 	"require_iat": True,
# 	"require_exp": True,
# 	"require_nbf": False,
# 	"require_iss": True,
# 	"require_sub": True,
# 	"require_jti": False,
# 	"require_at_hash": False,
# 	"leeway": 0,
# }

""" load config for passlib hashing from .ini file """
# pwd_context_making_changes = pwd_context.load_path(path=Path(__name__).resolve().parent / "services/CryptContext.ini")


# limiter = Limiter(key_func=get_ipaddr, default_limits=["3/minute"])



# async def create_token(jwt_claims: t_schema.JwtClaims):
# 	headers = {"alg": settings.ALGORITHM, "typ": "JWT"}
# 	if jwt_claims.jti is not None:
# 		jwt_claims.jti = str(jwt_claims.jti)
# 	token = jwt.encode(
# 		claims=jwt_claims.dict(exclude_none=True),
# 		headers=headers,
# 		key=settings.SECRET_KEY,
# 		algorithm=settings.ALGORITHM,
# 	)
# 	if jwt_claims.jti is not None:
# 		jwt_claims.jti = uuid.UUID(jwt_claims.jti)
# 	return token


# async def get_current_user(
# 	security_scopes: fast_security.SecurityScopes,
# 	token: str = fast_params.Depends(oauth2_scheme),
# 	db: sql_ses.Session = fast_params.Depends(base_ses.get_session)
# ) -> u_models.User:
# 	"""Returns Current Authenticated User And Check For Scopes In Token"""
# 	authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else f"Bearer"
# 	credentials_exception_need_detail = my_error.unauthorized_exception(authenticate_value)
# 	credentials_exception = credentials_exception_need_detail("Could not validate credentials")
# 	try:
# 		payload = jwt.decode(
# 			token=token,
# 			key=settings.SECRET_KEY,
# 			algorithms=[settings.ALGORITHM],
# 			audience=settings.FRONTEND_ORIGIN,
# 			issuer=settings.JWT_ISSUER,
# 			options=Jwt_Options
# 		)
# 		user_id: str = payload.get("sub")
# 		token_scopes_str: str = payload.get("scopes", None)
#
# 	except pydantic.ValidationError:
# 		raise credentials_exception
# 	except j_exc.ExpiredSignatureError:
# 		raise credentials_exception_need_detail("Token has been expired, you need to log in again")
# 	except j_exc.JWTClaimsError:
# 		raise credentials_exception_need_detail(" Token not valid")
# 	except j_exc.JWTError:
# 		raise credentials_exception
# 	user = db.get(u_models.User, ident=user_id)
# 	if user is None:
# 		raise credentials_exception_need_detail("No user for this token")
# 	# token_scopes = t_schema.SecurityScope(scope_str=token_scopes_str).scopes
# 	if "admin" in token_scopes_str:
# 		return user
# 	for scope in security_scopes.scopes:
# 		if scope not in token_scopes_str:
# 			raise credentials_exception_need_detail("Not enough permissions")
# 	return user
#
#
# async def get_current_active_user(
# 	current_user: u_models.User = fast_params.Security(get_current_user, scopes=["me"])
# ) -> u_models.User:
# 	if not current_user.is_active:
# 		raise my_error.inactive_user()
# 	return current_user
#
#
# def get_current_active_superuser(
# 	current_user: u_models.User = fast_params.Security(get_current_active_user, scopes=["admin"]),
# ) -> u_models.User:
# 	if not current_user.is_superuser:
# 		raise my_error.not_superuser()
# 	return current_user
