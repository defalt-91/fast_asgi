from typing import Any

from fastapi import Depends, HTTPException, Body, Security
from fastapi.routing import APIRouter
from pydantic import EmailStr
from services.password_service import get_password_hash
# from utils.emails_test import sent_id
from . import schemas
from services.security_service import get_current_active_superuser, get_current_active_user, get_current_user, get_db
from sqlalchemy.orm.session import Session
from core.base_settings import settings
from .models import User
from . import user_service
from . import models
from . import crud_user
from services.email_service import (
	send_email, send_new_account_email,
	send_reset_password_email,
	send_test_email, verify_password_reset_token,
	generate_password_reset_token,
)

accounts = APIRouter()


@accounts.post("/register", response_model=schemas.User)
async def create_user(*, user_created_back_data: User = Depends(user_service.create_user)):
	if user_created_back_data:
		return user_created_back_data


@accounts.post('/sudo', response_model=schemas.User)
async def create_superuser(*, user_created_back_data=Depends(user_service.create_superuser)):
	return user_created_back_data


@accounts.get("/profile", response_model=schemas.User)
async def read_users_me(*, current_user: schemas.User = Depends(get_current_active_user)) -> schemas.User:
	return current_user


@accounts.put("/me", response_model=schemas.User)
def update_user_me(user: models.User = Depends(user_service.update_user)) -> Any:
	return user


@accounts.get("/status/")
async def read_system_status():
	return {"status": "ok", "ao": settings.ALLOWED_HOSTS}


@accounts.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(get_db)) -> Any:
	"""
	Password Recovery
	"""
	user = crud_user.user.get_user_by_email(db, email=email)
	
	if not user:
		raise HTTPException(
			status_code=404,
			detail="The user with this email does not exist in the system.",
		)
	password_reset_token = generate_password_reset_token(email=email)
	send_reset_password_email(
		email_to=user.email,
		username=user.username,
		token=password_reset_token
	)
	return {"msg": "Password recovery email sent"}


@accounts.post("/reset-password/", response_model=schemas.Msg)
def reset_password(
	token: str = Body(...),
	new_password: str = Body(...),
	db: Session = Depends(get_db),
) -> Any:
	"""
	Reset password
	"""
	email = verify_password_reset_token(token)
	if not email:
		raise HTTPException(status_code=400, detail="Invalid token")
	user = crud_user.user.get_user_by_email(db, email=email)
	if not user:
		raise HTTPException(
			status_code=404,
			detail="The user with this username does not exist in the system.",
		)
	elif not crud_user.user.is_active(user):
		raise HTTPException(status_code=400, detail="Inactive user")
	hashed_password = get_password_hash(new_password)
	user.hashed_password = hashed_password
	db.add(user)
	db.commit()
	return {"msg": "Password updated successfully"}


@accounts.post("/register_mail", response_model=schemas.User)
def create_user(
	*,
	db: Session = Depends(get_db),
	user_in: schemas.UserCreate,
	current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
	"""
	Create new user.
	"""
	user = crud_user.user.get_user_by_email(db, email=user_in.email)
	if user:
		raise HTTPException(
			status_code=400,
			detail="The user with this username already exists in the system.",
		)
	user = crud_user.user.create(db, obj_in=user_in)
	if settings.EMAILS_ENABLED and user_in.email:
		send_new_account_email(
			email_to=user_in.email, username=user_in.email, password=user_in.password1
		)
	return user


@accounts.post("/open", response_model=schemas.User)
def create_user_open(
	*,
	db: Session = Depends(get_db),
	password: str = Body(...),
	email: EmailStr = Body(...),
	full_name: str = Body(None),
) -> Any:
	"""
	Create new user without the need to be logged in.
	"""
	if not settings.USERS_OPEN_REGISTRATION:
		raise HTTPException(
			status_code=403,
			detail="Open user registration is forbidden on this server",
		)
	user = crud_user.user.get_user_by_email(db, email=email)
	if user:
		raise HTTPException(
			status_code=400,
			detail="The user with this username already exists in the system",
		)
	user_in = schemas.UserCreate(raw_password=password, email=email, full_name=full_name)
	user = crud_user.user.create(db, obj_in=user_in)
	return user


@accounts.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
	user_id: int,
	current_user: models.User = Depends(get_current_active_user),
	db: Session = Depends(get_db),
) -> Any:
	"""
	Get a specific user by id.
	"""
	user = crud_user.user.get(db, id=user_id)
	if user == current_user:
		return user
	if not crud_user.user.is_superuser(current_user):
		raise HTTPException(
			status_code=400, detail="The user doesn't have enough privileges"
		)
	return user


@accounts.put("/{user_id}", response_model=schemas.User)
def update_user(
	*,
	db: Session = Depends(get_db),
	user_id: int,
	user_in: schemas.UserUpdate,
	current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
	"""
	Update a user.
	"""
	user = crud_user.user.get(db, id=user_id)
	if not user:
		raise HTTPException(
			status_code=404,
			detail="The user with this username does not exist in the system",
		)
	user = crud_user.user.update(db, db_obj=user, obj_in=user_in)
	return user


@accounts.get("/profile/items/")
async def read_own_items(current_user: schemas.User = Security(get_current_active_user, scopes=["items"])):
	return [{"item_id": "Foo", "owner": current_user.email}]


# @accounts.post('/testmail')
# async def sent_test_mail(
# 	email: str = 'armansoltanian@gmail.com',
# 	username: str = 'defii',
# 	password1: str = 'test_password',
# ):
# 	a = sent_id()
# 	return {'ok': a}
