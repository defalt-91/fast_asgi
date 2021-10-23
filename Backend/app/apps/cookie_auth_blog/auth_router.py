from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
import base64
from apps.token.schemas import Token
from apps.users.models import User
from core.base_settings import settings
from apps.cookie_auth_blog.basic_authentication import BasicAuth, basic_auth
from fastapi.routing import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from datetime import timedelta
from fastapi import Depends, HTTPException
from starlette.responses import RedirectResponse, Response, JSONResponse
from services.db_service import get_db
from services.security_service import create_access_token, get_current_active_user
from apps.users import crud_user

blog_router = APIRouter()


@blog_router.get("/login_basic")
async def login_basic(auth: BasicAuth = Depends(basic_auth)):
	if not auth:
		response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
		return response
	
	try:
		decoded = base64.b64decode(auth).decode("ascii")
		username, _, password = decoded.partition(":")
		user = crud_user.user.authenticate_user(username, password, db=Depends(get_db))
		if not user:
			raise HTTPException(status_code=400, detail="Incorrect email or password")
		
		access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
		access_token = create_access_token(
				data={"sub": username}, expires_delta=access_token_expires
		)
		
		token = jsonable_encoder(access_token)
		
		response = RedirectResponse(url="/docs")
		response.set_cookie(
				"Authorization",
				value=f"Bearer {token}",
				domain="localtest.me",
				httponly=True,
				max_age=1800,
				expires=1800,
		)
		return response
	
	except :
		response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
		return response


@blog_router.get("/logout")
async def route_logout_and_remove_cookie():
	response = RedirectResponse(url="/")
	response.delete_cookie("Authorization", domain="localtest.me")
	return response


@blog_router.get("/")
async def homepage():
	return "Welcome to the security test!"


@blog_router.get("/openapi.json")
async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
	return JSONResponse(get_openapi(title="FastAPI", version='1', routes=blog_router.routes))


@blog_router.get("/docs")
async def get_documentation(current_user: User = Depends(get_current_active_user)):
	return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@blog_router.post("/token", response_model=Token)
async def route_login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
	user = crud_user.user.authenticate_user(db=Depends(get_db), email=form_data.username, password=form_data.password)
	if not user:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
			data={"sub": user.username}, expires_delta=access_token_expires
	)
	return {"access_token": access_token, "token_type": "bearer"}


@blog_router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
	return current_user


@blog_router.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
	return [{"item_id": "Foo", "owner": current_user.username}]
