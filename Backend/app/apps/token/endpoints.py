from datetime import timedelta
from typing import Any

from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException
from fastapi import Response
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestFormStrict
from starlette import status

from services.db_service import get_db
from services.security_service import create_access_token, get_current_user
from core.base_settings import settings
from apps.users import crud_user
from ..users import models,schemas

token_router = APIRouter()


@token_router.post("/token")
async def authorization_server(
	response: Response,
	form_data: OAuth2PasswordRequestFormStrict = Depends(),
	db: Session = Depends(get_db),
):
	user = crud_user.user.authenticate_by_username(
		db=db,
		username=form_data.username,
		password=form_data.password
	)
	# elif form_data.email:
	# 	user = crud_user.authenticate_by_email(
	# 			db=db,
	# 			username=form_data.username,
	# 			password=form_data.password
	# 	)
	
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"}
		)
	elif not crud_user.user.is_active(user):
		raise HTTPException(status_code=400, detail="Inactive user")
	access_token = create_access_token(
		data={"sub": user.username, "scopes": form_data.scopes},
		expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
	)
	response.set_cookie(
		key='authorization',
		value=f"bearer {access_token}",
		httponly=True,
		samesite="strict",
		secure=False,
		expires=settings.ACCESS_TOKEN_EXPIRATION_MINUTES * 60,
		domain="api.myawesomesite.io",
		path='/'
	)
	return {"response": "asd"}


@token_router.post("/verify", response_model=schemas.User)
async def test_token(current_user: models.User = Depends(get_current_user)) -> Any:
	"""
	Test access token
	"""
	return current_user
