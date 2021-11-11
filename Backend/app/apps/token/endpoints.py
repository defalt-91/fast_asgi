import typing
import sqlalchemy.orm.session as orm_ses
import fastapi.exceptions as fast_exc
import fastapi.security.oauth2 as fast_oauth
import fastapi.param_functions as fast_param
import fastapi.routing as fast_routing
import pydantic.networks as py_net

from services.scopes import ScopeTypes
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
import events.emmiters as emit


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


AccessTokenClaimsFactory = t_schemas.AccessClaimsFactory()
RefreshTokenClaimsFactory = t_schemas.RefreshClaimsFactory()


@token_router.post("/token", response_model=t_schemas.TokenResponse, response_model_exclude_none=True)
@security_service.limiter.limit("125/minutes")
async def authorization_server(
	request: st_req.Request,
	claims_with_access_token: t_schemas.JwtClaims = fast_param.Depends(tok_deps.login_handler)
) -> t_schemas.TokenResponse:
	return t_schemas.TokenResponse(
		expiration_datetime=claims_with_access_token.exp,
		access_token=claims_with_access_token.token,
	)


@token_router.post(
	"/refresh",
	status_code=s_status.HTTP_200_OK,
	response_model=t_schemas.TokenResponse,
	response_model_exclude_none=True
)
async def get_new_access_token(
	token_claims: t_schemas.JwtClaims = fast_param.Depends(tok_deps.access_token_from_refresh_token)
) -> t_schemas.TokenResponse:
	return t_schemas.TokenResponse(
		access_token=token_claims.token,
		expiration_datetime=token_claims.exp
	)


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
