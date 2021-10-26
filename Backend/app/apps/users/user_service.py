from typing import Any, Tuple

from apps.users import models
from core.base_settings import settings
from services.db_service import get_db
from sqlalchemy.orm.session import Session
from fastapi import Depends, Body, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from apps.users import crud_user
from services.paginator import Pagination
from services.security_service import get_current_active_user, get_current_active_superuser
from . import schemas
from pydantic import EmailStr
from services.email_service import send_new_account_email
from .permissions import UserIsCurrentOrSudo
from ..scopes.models import Scope


async def user_list(
	db: Session = Depends(get_db),
	pagination: Tuple[int, int] = Depends(Pagination.page_size),
	current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
	""" Retrieve users. """
	skip, limit = pagination
	users = crud_user.user.get_multi(db=db, limit=limit, skip=skip)
	return users


async def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
	""" Create new user without the need to be logged in. """
	if not settings.USERS_OPEN_REGISTRATION:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Open user registration is forbidden on this server",
		)
	conflict_username = crud_user.user.get_user_by_username(db=db, username=user_in.username)
	if conflict_username:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="The user with this username already exists in the system.",
		)
	if user_in.email:
		conflict_email = crud_user.user.get_user_by_email(db=db, email=user_in.email)
		if conflict_email:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="The user with this email already exists in the system.",
			)
	user_in.is_superuser = False
	me = db.query(Scope).filter(Scope.id == 1).first()
	posts = db.query(Scope).filter(Scope.id == 2).first()
	
	user_in.is_superuser = True
	user_in_db = crud_user.user.create(db=db, obj_in=user_in)
	if settings.EMAILS_ENABLED and user_in.email:
		send_new_account_email(
			email_to=user_in.email, username=user_in.email, password=user_in.password1
		)
	user_in_db.scopes.append(me)
	user_in_db.scopes.append(posts)
	db.add(user_in_db)
	db.commit()
	db.refresh(user_in_db)
	return user_in_db


async def create_superuser(
	user_in: schemas.UserCreate,
	current_user=Depends(get_current_active_superuser),
	db: Session = Depends(get_db)
):
	if user_in.email:
		conflict_email = crud_user.user.get_user_by_email(db=db, email=user_in.email)
		if conflict_email:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="The user with this email already exists in the system.",
			)
	conflict_username = crud_user.user.get_user_by_username(db=db, username=user_in.username)
	if conflict_username:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="The user with this username already exists in the system.",
		)
	user_in.is_superuser = True
	
	user = crud_user.user.create(db=db, obj_in=user_in)
	if not user:
		raise HTTPException(detail='something is wrong', status_code=status.HTTP_400_BAD_REQUEST)
	admin = db.query(Scope).filter(Scope.id == 3).first()
	user.scopes.append(admin)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user


async def update_user_me(
	*,
	db: Session = Depends(get_db),
	password1: str = Body(None),
	password2: str = Body(None),
	full_name: str = Body(None),
	email: EmailStr = Body(None),
	current_user: models.User = Depends(get_current_active_user),
) -> models.User:
	""" Update own user. """
	current_user_data = jsonable_encoder(current_user)
	user_in = schemas.UserUpdate(**current_user_data)
	if password1 is not None:
		user_in.password1 = password1
	if password2 is not None:
		user_in.password2 = password2
	if full_name is not None:
		user_in.full_name = full_name
	if email is not None:
		user_in.email = email
	user = crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
	return user


def read_user_me(
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user), ) -> Any:
	""" Get current user. """
	return current_user


def read_user_by_id(
	*,
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_user),
	user_id: int = Query(...)
) -> Any:
	""" Get a specific user by id. """
	
	user = crud_user.user.get(db=db, id=user_id)
	if not user:
		raise HTTPException(detail='User doesnt exist !', status_code=status.HTTP_400_BAD_REQUEST)
	UserIsCurrentOrSudo(current_user=current_user, user=user).has_permission()
	return user


def update_user_by_id(
	*,
	db: Session = Depends(get_db),
	user_id: int,
	user_in: schemas.UserUpdate,
	current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
	""" Update a user. """
	user = crud_user.user.get(db, id=user_id)
	if not user:
		raise HTTPException(
			status_code=404,
			detail="The user with this username does not exist in the system",
		)
	user = crud_user.user.update(db=db, db_obj=user, obj_in=user_in)
	return user


def deactivate_user_by_id(
	user_id: int,
	user_in: schemas.UserUpdate,
	db: Session = Depends(get_db),
	current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
	db_user = crud_user.user.get(db=db, id=user_id)
	if not db_user:
		raise HTTPException(
			status_code=404,
			detail="The user with this username does not exist in the system",
		)
	# obj_in = (** user.dict())
	returned = crud_user.user.deactivate(db=db, db_obj=db_user, obj_in=user_in)
	return returned
