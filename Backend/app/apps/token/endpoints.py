from typing import Any, List, Optional
from sqlalchemy.orm.session import Session
from fastapi import Depends, Request, Response, APIRouter, HTTPException, Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from dataclasses import dataclass, field

from core.base_settings import get_settings
from core.database.session import get_session
from services import security_service, email_service, errors, scopes, password_service
from .TokenDAL import token_dal
from .schemas import AccessTokenJwtClaims, TokenScopesTypes
import apps.scopes.models as scope_model
import apps.scopes.schemas as scope_schema
from ..users import models, schemas, UserDAL


settings = get_settings()

token_router = APIRouter()


@dataclass
class TestDataclasses:
	id: Optional[int] = Body(default=52, description='id of user', ge=12)
	last_name: str = field(default="your family name")
	name: str = field(default='your name')


@token_router.post('/dataclasses')
async def using_dataclasses(usr: TestDataclasses):
	return usr


@token_router.post("/verify", response_model=schemas.User, response_model_exclude={"is_superuser", "is_active"}, )
@security_service.limiter.limit("5/minutes")
async def test_token(
	request: Request, a=Depends(get_session), current_user: models.User = Depends(security_service.get_current_user)
) -> Any:
	"""Test access token and get user details"""
	return current_user


@token_router.post("/password-recovery/{email}", response_model=schemas.Msg)
@security_service.limiter.limit("5/minutes")
def recover_password(request: Request, *, email: EmailStr = Query(...), db: Session = Depends(get_session)):
	"""Password Recovery"""
	user = UserDAL.user_dal.get_user_by_email(session=db, email=email)
	if not user:
		raise HTTPException(status_code=404, detail="The user with this email does not exist in the system.")
	password_reset_token = email_service.generate_password_reset_token(email=email)
	email_service.send_reset_password_email(email_to=user.email, username=user.username, token=password_reset_token)
	return {"msg": "Password recovery email sent"}


@token_router.post("/reset-password/", response_model=schemas.Msg)
@security_service.limiter.limit("5/minutes")
def reset_password(
	request: Request, token: str = Body(...), new_password: str = Body(...),
	db: Session = Depends(get_session), ) -> Any:
	"""Reset password"""
	email = email_service.verify_password_reset_token(token)
	if not email:
		raise HTTPException(status_code=400, detail="Invalid token")
	user = UserDAL.user_dal.get_user_by_email(session=db, email=email)
	if not user:
		raise errors.user_not_exist_username()
	if not user.is_authenticated:
		raise errors.inactive_user()
	hashed_password = password_service.get_password_hash(new_password)
	user.hashed_password = hashed_password
	UserDAL.user_dal.save(session=db, obj=user)
	return {"msg": "Password updated successfully"}


@token_router.post("/token")
@security_service.limiter.limit("5/minutes")
async def authorization_server(
	request: Request,
	response: Response,
	form_data: OAuth2PasswordRequestForm = Depends(),
	session: Session = Depends(get_session),
) -> Any:
	user: Optional[models.User] = UserDAL.user_dal.authenticate_by_username(
		session=session, username=form_data.username, raw_password=form_data.password
	)
	if not user:
		raise errors.incorrect_username_or_password()
	if not user.is_authenticated:
		raise errors.inactive_user()
	
	allowed_scopes: List[scopes.ScopeTypes] = []
	user_scopes: List[scope_model.Scope] = user.scopes
	if user.is_superuser:
		allowed_scopes.append(TokenScopesTypes.ADMIN.value)
	else:
		for i in user_scopes:
			j = scope_schema.ScopeOut.from_orm(i)
			allowed_scopes.append(j.code)
	# admin scope is just enough
	
	# for scope in form_data.scopes:
	# 	if scope.lower() == 'me':
	# 		allowed_scopes.append('me')
	# 	if scope.lower() == 'posts':
	# 		allowed_scopes.append('posts')
	claims_pyd = AccessTokenJwtClaims(sub=user.username, scopes=allowed_scopes)
	access_token = security_service.create_access_token(claims_pyd)
	response.set_cookie(
		key="authorization",
		value=f"bearer {access_token}",
		httponly=True,
		samesite="strict",  # sending just to the site that wrote the cookie
		secure=False,
		expires=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
		# domain="myawesomesite.io",  # subdomains are ignored , like api.myawesomesite.io ... just the domain in
		# needed
		path="/",
	)
	# token = Token()
	# token.jwt = access_token
	# token.token_type = TokenTypes.ACCESS_TOKEN
	# token.user_id = user.id
	# token.jti = claims_pyd.jti
	# session.add(token)
	# session.commit()
	# session.refresh(token)
	return access_token


@token_router.get("/{user_id}", dependencies=[Depends(security_service.get_current_user)])
async def user_tokens(
	user_id: int,
	session: Session = Depends(get_session),
):
	token_list = token_dal.get_access_token(session=session, user_id=user_id)
	if not token_list:
		raise errors.user_have_not_active_token()
	return token_list
