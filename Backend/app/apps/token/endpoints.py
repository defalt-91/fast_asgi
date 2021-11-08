import typing
import sqlalchemy.orm.session as orm_ses
import fastapi.exceptions as fast_exc
import fastapi.security.oauth2 as fast_oauth
import fastapi.param_functions as fast_param
import fastapi.routing as fast_routing
import pydantic.networks as py_net
from .TokenDAL import token_dal
import core.base_settings as base_setting
import core.database.session as base_ses
import apps.users.models as u_models
import apps.users.schemas as u_schemas
import apps.token.schemas as t_schemas
import services.security_service as security_service
import services.email_service as email_service
import services.errors as errors
import services.password_service as password_service
import starlette.status as s_status
import apps.token.deps as tok_deps
import starlette.requests as st_req
import starlette.responses as st_res
from apps.users.UserDAL import user_dal


settings = base_setting.get_settings()

token_router = fast_routing.APIRouter()


@token_router.post("/verify", response_model=u_schemas.User, response_model_exclude={"is_superuser", "is_active"}, )
@security_service.limiter.limit("5/minutes")
async def test_token(
	request: st_req.Request,
	current_user: u_models.User = fast_param.Depends(security_service.get_current_user),
) -> typing.Any:
	"""Test access token and get user details"""
	return current_user


@token_router.post("/password-recovery/{email}", response_model=u_schemas.Msg)
@security_service.limiter.limit("5/minutes")
def recover_password(
	*, request: st_req.Request, email: py_net.EmailStr = fast_param.Query(...),
	db: orm_ses.Session = fast_param.Depends(base_ses.get_session), ):
	"""Password Recovery"""
	user = user_dal.check_email_exist(session=db, email=email)
	if not user:
		raise fast_exc.HTTPException(
			status_code=404,
			detail="The user with this email does not exist in the system.",
		)
	password_reset_token = email_service.generate_password_reset_token(email=email)
	email_service.send_reset_password_email(
		email_to=user.email, username=user.username, token=password_reset_token
	)
	return {"msg": "Password recovery email sent"}


@token_router.post("/reset-password/", response_model=u_schemas.Msg)
@security_service.limiter.limit("5/minutes")
def reset_password(
	request: st_req.Request, token: str = fast_param.Body(...),
	new_password: str = fast_param.Body(...),
	db: orm_ses.Session = fast_param.Depends(base_ses.get_session), ) -> typing.Any:
	"""Reset password"""
	email = email_service.verify_password_reset_token(token)
	if not email:
		raise fast_exc.HTTPException(status_code=400, detail="Invalid token")
	user = user_dal.get(session=db, email=email)
	if not user:
		raise errors.user_not_exist_username()
	if not user.is_authenticated:
		raise errors.inactive_user()
	hashed_password = password_service.get_password_hash(new_password)
	user.hashed_password = hashed_password
	user_dal.save(session=db, obj=user)
	return {"msg": "Password updated successfully"}


@token_router.post("/token")
@security_service.limiter.limit("5/minutes")
async def authorization_server(
	request: st_req.Request,
	response: st_res.Response,
	form_data: fast_oauth.OAuth2PasswordRequestForm = fast_param.Depends(),
	session: orm_ses.Session = fast_param.Depends(base_ses.get_session),
) -> typing.Any:
	user: typing.Optional[u_models.User] = user_dal.authenticate(
		session=session, username=form_data.username, raw_password=form_data.password
	)
	if not user:
		raise errors.incorrect_username_or_password()
	if not user.is_authenticated:
		raise errors.inactive_user()
	
	allowed_scopes = await tok_deps.add_user_scopes(user=user)
	# for scope in form_data.scopes:
	# 	if scope.lower() == 'me':
	# 		allowed_scopes.append('me')
	# 	if scope.lower() == 'posts':
	# 		allowed_scopes.append('posts')
	access_claims = t_schemas.AccessTokenJwtClaims(
		sub=user.username, scopes=allowed_scopes
	)
	if user.is_admin:
		access_claims.admin = True
	access_token = security_service.create_access_token(access_claims)
	refresh_claims = t_schemas.RefreshTokenJwtClaims(sub=user.username)
	refresh_token = security_service.create_refresh_token(token_claims=refresh_claims)
	response.set_cookie(
		key="refresh_token",
		value=f"{refresh_token}",
		httponly=True,
		samesite="strict",  # sending just to the site that wrote the cookie
		secure=False,
		expires=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
		# domain="myawesomesite.io",  # subdomains are ignored , like api.myawesomesite.io ... just the domain in
		# needed
		path="/",
	)
	token_dal.create_refresh_token(
		session=session,
		refresh_claims=refresh_claims,
		user_id=user.id,
		refresh_token=refresh_token,
	)
	# tokens = token_dal.get_multi_with_user(session=session, sub=user.id)
	# for token in tokens:
	# 	session.delete(token)
	# session.commit()
	return {
		"token_type": "bearer",
		"access_token": access_token.access_token,
		"access_token_exp_timestamp": access_claims.exp_timestamp,
		"access_token_exp_date": access_claims.exp,
		"refresh_token": {
			"token_type": "refresh_token",
			"token": refresh_token,
			"exp_date": refresh_claims.exp,
			"exp_timestamp": refresh_claims.exp_timestamp,
		},
	}


@token_router.post(
	"/refresh",
	status_code=s_status.HTTP_200_OK,
	response_model=t_schemas.AccessRefreshedForResponse,
	response_model_include={'access_token', 'expiration_time', 'audience', 'token_type', 'expiration_timestamp'}
)
async def get_new_access_token(
	session: orm_ses.Session = fast_param.Depends(base_ses.get_session),
	refresh_token: tok_deps.oauth2_refresh_token = fast_param.Depends(),
) -> typing.Optional[t_schemas.AccessRefreshedForResponse]:
	access_token_with_claims = await tok_deps.access_token_from_refresh_token(
		session=session, refresh_token=refresh_token
	)
	return access_token_with_claims


@token_router.get("/{user_id}")
async def user_refresh_tokens(
	user_id: int,
	current_user: u_models.User = fast_param.Security(security_service.get_current_active_superuser),
	session: orm_ses.Session = fast_param.Depends(base_ses.get_session)
):
	if not current_user.id == user_id:
		raise fast_exc.HTTPException(
			status_code=s_status.HTTP_403_FORBIDDEN,
			detail="You are not authorize to see this user tokens"
		)
	token_list = token_dal.get_access_tokens(session=session, user_id=user_id)
	if not token_list:
		raise errors.user_have_not_active_token()
	return token_list
