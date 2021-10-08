from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from .schemas import Token
from services.security import (
	authenticate_user,
	create_access_token,
	pwd_context,
)
from core.base_settings import settings
token_router = APIRouter()

fake_users_db = {
		"defalt91": {
				"username"       : "defalt91", "full_name": "John Doe", "email": "johndoe@example.com",
				"hashed_password": pwd_context.hash("secret"),
				"is_active"      : False,
		}
}


# /token
@token_router.post("/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
	user = authenticate_user(
			db=fake_users_db,
			username=form_data.username,
			password=form_data.password
	)
	if not user:
		raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect username or password",
				headers={"WWW-Authenticate": "Bearer"}
		)
	access_token = create_access_token(
			data={"sub": user.username, "scopes": form_data.scopes},
			expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
	)
	return {"access_token": access_token, "token_type": "bearer"}
