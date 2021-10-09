from datetime import timedelta
from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from services.db_service import get_db
from .schemas import Token
from services.security import (
	create_access_token,
)
from core.base_settings import settings
from ..users.crud_user import user as crud_user

token_router = APIRouter()


# /token
@token_router.post("/", response_model=Token)
async def login_for_access_token(
		form_data: OAuth2PasswordRequestForm = Depends(),
		db: Session = Depends(get_db)
):
	user = crud_user.authenticate(
			db=db,
			email=form_data.username,
			password=form_data.password
	)
	if not user:
		raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect username or password",
				headers={"WWW-Authenticate": "Bearer"}
		)
	form_data.scopes.append('me')
	print(form_data.scopes)
	access_token = create_access_token(
			data={"sub": user.email, "scopes": form_data.scopes},
			expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
	)
	return {"access_token": access_token, "token_type": "bearer"}
