from typing import Any, Optional

from apps.users.schemas import UserCreate
from apps.users import models
from services.db_service import get_db
from sqlalchemy.orm.session import Session
from fastapi import Depends, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from apps.users import crud_user
from services.security_service import get_current_active_user
from . import schemas
from pydantic import EmailStr


async def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> models.User:
	conflict_username = crud_user.user.get_user_by_username(db=db, username=user_in.username)
	if user_in.email:
		conflict_email = crud_user.user.get_user_by_email(db=db, email=user_in.email)
		if conflict_email:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="The user with this email already exists in the system.",
			)
	if conflict_username:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="The user with this username already exists in the system.",
		)
	user_in_db = crud_user.user.create(db=db, obj_in=user_in)
	return user_in_db


async def create_superuser(user_in: UserCreate, db: Session = Depends(get_db)):
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
	user = crud_user.user.create_superuser(obj_in=user_in, db=db)
	if not user:
		raise HTTPException(detail='something is wrong', status_code=status.HTTP_400_BAD_REQUEST)
	
	return user


class Permissions:
	@staticmethod
	def IsAuthor(
		current_user: Optional[models.User] = None,
		db_obj: Optional[Any] = None,
		obj_author_username: Optional[str] = None
	):
		if db_obj:
			print('current user')
			return current_user.username == db_obj.author.username
		elif obj_author_username:
			print('username')
			return obj_author_username == current_user.username


async def update_user(
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
