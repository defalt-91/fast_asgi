from datetime import timedelta

from typing import Any, List

from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException, Request
from fastapi import Response
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestFormStrict, OAuth2PasswordRequestForm
from starlette import status

from . import deps
from services.db_service import get_db
from services.security_service import create_access_token, get_current_user, limiter
from core.base_settings import settings
from apps.users import crud_user
from ..scopes.models import Scope

from ..users import models, schemas

token_router = APIRouter()


@token_router.post("/token")
@limiter.limit("5/minutes")
async def authorization_server(
	request: Request,
	response: Response,
	form_data: OAuth2PasswordRequestForm = Depends(),
	db: Session = Depends(get_db),
) -> Any:
	user = crud_user.user.authenticate_by_username(
		db=db,
		username=form_data.username,
		password=form_data.password
	)
	print(request.client)
	print(request.client.host)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"}
		)
	if not crud_user.user.is_active(user):
		raise HTTPException(status_code=400, detail="Inactive user")
	
	allowed_scopes: List[str] = []
	user_scopes: List[Scope] = user.scopes
	if not user.is_superuser:
		for i in user_scopes:
			allowed_scopes.append(i.code)
	else:
		# admin scope is just enough
		allowed_scopes.append('admin')
	
	# for scope in form_data.scopes:
	# 	if scope.lower() == 'me' and user.is_active:
	# 		allowed_scopes.append('me')
	# 	else:
	# 		raise HTTPException(detail='This account is disabled !', status_code=status.HTTP_403_FORBIDDEN)
	# 	if scope.lower() == 'posts' and user.is_active:
	# 		allowed_scopes.append('posts')
	
	access_token = create_access_token(
		data={"sub": user.username, "scopes": allowed_scopes},
		expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
	)
	response.set_cookie(
		key='authorization',
		value=f"bearer {access_token}",
		httponly=True,
		samesite="strict",  # sending just to the site that wrote the cookie
		secure=False,
		expires=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
		# domain="myawesomesite.io",  # subdomains are ignored , like api.myawesomesite.io ... just the domain in needed
		path='/'
	)
	return {
		"access_token": access_token,
		"token_type": "bearer",
	}


@token_router.post("/verify", response_model=schemas.User, response_model_exclude={'is_superuser', 'is_active'})
@limiter.limit("5/minutes")
async def test_token(request: Request, current_user: models.User = Depends(get_current_user)) -> Any:
	""" Test access token and get user details """
	return current_user


@token_router.post("/password-recovery/{email}", response_model=schemas.Msg)
@limiter.limit("5/minutes")
def recover_password(request: Request, *, msg=Depends(deps.password_recover)) -> Any:
	return msg


@token_router.post("/reset-password/", response_model=schemas.Msg)
@limiter.limit("5/minutes")
def reset_password(request: Request, *, msg=Depends(deps.reset_password)):
	return msg
