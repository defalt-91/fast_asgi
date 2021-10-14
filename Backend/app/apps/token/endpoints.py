from datetime import timedelta
from typing import Optional

from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException
from fastapi import Response
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestFormStrict
from starlette import status

from services.db_service import get_db
from .crud_token import init_token
from .schemas import Token, TokenCreate
from services.security import create_access_token
from core.base_settings import settings
from apps.users.crud_user import user as crud_user
from fastapi import Form
from fastapi.responses import RedirectResponse
from .models import Token as TokenModel

token_router = APIRouter()


class Oauth2PasswordGrandTypeRequestForm:
	def __init__(
			self,
			grant_type: str = Form("password", regex="password"),
			username: str = Form(...),
			email: str = Form(None),
			password: str = Form(...),
			scope: str = Form(""),
			client_id: Optional[str] = Form(None),
			client_secret: Optional[str] = Form(None),
	):
		self.grant_type = grant_type
		self.username = username
		self.password = password
		self.email = email
		self.scopes = scope.split()
		self.client_id = client_id
		self.client_secret = client_secret


# authorize
@token_router.post("/authorize")
async def authorization_server(
		redirect_uri: str ,
		client_id: str,
		response_type: Optional[str] = 'code',
		scope: Optional[str] = None,
		state: Optional[str] = None,
		client_secret: Optional[str] = None,
		form_data: Oauth2PasswordGrandTypeRequestForm = Depends(),
		db: Session = Depends(get_db),
):
	if form_data.username:
		user = crud_user.authenticate_by_username(
				db=db,
				username=form_data.username,
				password=form_data.password
		)
	elif form_data.email:
		user = crud_user.authenticate_by_email(
				db=db,
				username=form_data.username,
				password=form_data.password
		)
	
	if not user:
		raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect username or password",
				headers={"WWW-Authenticate": "Bearer"}
		)
	if 'me' not in form_data.scopes:
		form_data.scopes.append('me')
	
	# response.set_cookie(key='authorization', value=f"bearer {access_token}")
	# return {"access_token": access_token, "token_type": "bearer"}
	access_token = create_access_token(
			data={"sub": user.username, "scopes": form_data.scopes},
			expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES),
	)
	object_in = TokenCreate(jwt=access_token, user_id=user.id)
	token_hole = init_token.create(obj_in=object_in)
	
	return RedirectResponse(
			url=redirect_uri,
			headers={
					'code': token_hole.id,
			}
	)


# /token
@token_router.post("/token", response_model=Token)
async def login_for_access_token(
		code: Optional[int],
		response: Response,
		db: Session = Depends(get_db)

):
	authorization_code = db.query(TokenModel).get(id=code)
	response.set_cookie(key='authorization', value=f"bearer {authorization_code.jwt}")
	if authorization_code:
		return {"access_token": authorization_code.jwt, "token_type": "bearer"}
	else:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not authorized to this page")
