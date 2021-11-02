from datetime import timedelta
from typing import Any, List, Optional
from sqlalchemy.orm.session import Session
from fastapi import Depends, Request, Response, APIRouter, HTTPException, Query, Body
from fastapi.security import OAuth2PasswordRequestFormStrict, OAuth2PasswordRequestForm

from services.security_service import create_access_token, get_current_user, limiter
from core.base_settings import settings
from .TokenDAL import token_dal
from .models import Token, TokenTypes
from .schemas import TokenCreate
from ..scopes.models import Scope
from ..users import models, schemas
from ..users.UserDAL import user_dal
from core.database.session import get_session
from services import errors
from services.email_service import (
	generate_password_reset_token,
	send_reset_password_email,
	verify_password_reset_token,
)
from pydantic import EmailStr
from services.password_service import get_password_hash
from dataclasses import dataclass, field


token_router = APIRouter()


@dataclass
class TestDataclasses:
	id: Optional[int] = Body(default=52,description='id of user',ge=12	)
	last_name: str = field(default="your family name")
	name: str = field(default='your name')


@token_router.post('/dataclasses')
async def using_dataclasses(usr: TestDataclasses):
	return usr

@token_router.post(
	"/verify",
	response_model=schemas.User,
	response_model_exclude={"is_superuser", "is_active"},
)
@limiter.limit("5/minutes")
async def test_token(
	request: Request, current_user: models.User = Depends(get_current_user)
) -> Any:
	"""Test access token and get user details"""
	return current_user


@token_router.post("/password-recovery/{email}", response_model=schemas.Msg)
@limiter.limit("5/minutes")
def recover_password(
	request: Request,
	*,
	email: EmailStr = Query(...),
	db: Session = Depends(get_session),
):
	"""Password Recovery"""
	user = user_dal.get_user_by_email(session=db, email=email)
	if not user:
		raise HTTPException(
			status_code=404,
			detail="The user with this email does not exist in the system.",
		)
	password_reset_token = generate_password_reset_token(email=email)
	send_reset_password_email(
		email_to=user.email, username=user.username, token=password_reset_token
	)
	return {"msg": "Password recovery email sent"}


@token_router.post("/reset-password/", response_model=schemas.Msg)
@limiter.limit("5/minutes")
def reset_password(
	request: Request,
	token: str = Body(...),
	new_password: str = Body(...),
	db: Session = Depends(get_session),
) -> Any:
	"""Reset password"""
	email = verify_password_reset_token(token)
	if not email:
		raise HTTPException(status_code=400, detail="Invalid token")
	user = user_dal.get_user_by_email(session=db, email=email)
	if not user:
		raise errors.user_not_exist_username
	if not user_dal.is_active(user):
		raise errors.inactive_user
	hashed_password = get_password_hash(new_password)
	user.hashed_password = hashed_password
	db.add(user)
	db.commit()
	return {"msg": "Password updated successfully"}


@token_router.post("/token")
@limiter.limit("5/minutes")
async def authorization_server(
	request: Request,
	response: Response,
	form_data: OAuth2PasswordRequestForm = Depends(),
	session: Session = Depends(get_session),
) -> Any:
	user = user_dal.authenticate_by_username(
		session=session, username=form_data.username, raw_password=form_data.password
	)
	if not user:
		raise errors.incorrect_username_or_password
	if not user.is_active:
		raise errors.inactive_user
	
	allowed_scopes: List[str] = []
	user_scopes: List[Scope] = user.scopes
	if user.is_superuser:
		allowed_scopes.append("admin")
	else:
		for i in user_scopes:
			allowed_scopes.append(i.code)
	# admin scope is just enough
	
	# for scope in form_data.scopes:
	# 	if scope.lower() == 'me' and user.is_active:
	# 		allowed_scopes.append('me')
	# 	else:
	# 		raise HTTPException(detail='This account is disabled !', status_code=status.HTTP_403_FORBIDDEN)
	# 	if scope.lower() == 'posts' and user.is_active:
	# 		allowed_scopes.append('posts')
	
	token = Token()
	token.token_type = TokenTypes.ACCESS_TOKEN
	token.user_id = user.id
	session.add(token)
	session.commit()
	session.refresh(token)
	access_token = create_access_token(
		using_jti=True,
		jti=token.id,
		data={"sub": user.username, "scopes": allowed_scopes},
		expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
	)
	token.jwt = access_token
	session.add(token)
	session.commit()
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
	
	return token


@token_router.get("/{user_id}")
async def user_tokens(
	user_id: int,
	session: Session = Depends(get_session),
	current_user: models.User = Depends(get_current_user),
):
	token_list = token_dal.get_access_token(session=session, user_id=user_id)
	if not token_list:
		raise errors.user_have_not_active_token
	return token_list
