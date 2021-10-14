from typing import Any, Optional

from apps.users.schemas import User, UserCreate
from apps.users.models import User as UserModel
from services.db_service import get_db
from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException, status
from apps.users import crud_user


async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
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
	user = crud_user.user.create_superuser(obj_in=user_in, db=db)
	return user


class Permissions:
	@staticmethod
	def IsAuthor(
		current_user: Optional[UserModel] = None,
		db_obj: Optional[Any] = None,
		obj_author_username: Optional[str] = None
	):
		if db_obj:
			print('current user')
			return current_user.username == db_obj.author.username
		elif obj_author_username:
			print('username')
			return obj_author_username == current_user.username
