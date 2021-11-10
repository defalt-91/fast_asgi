from __future__ import annotations

from services.base_dal import BaseDAL
from .models import User
from . import schemas
from typing import Optional, Union, Dict, List, Any
from sqlalchemy.orm.session import Session
from services.password_service import get_password_hash, verify_password
from apps.scopes import models
from sqlalchemy import select
from pydantic import EmailStr
import fastapi.security.oauth2 as f_oauth
import fastapi.param_functions as f_params


class UserDAL(BaseDAL[User, schemas.UserCreate, schemas.UserUpdate]):
	def create(self, session: Session, obj_in: schemas.UserCreate) -> Optional[User]:
		password_hash = get_password_hash(obj_in.password2)
		user = User()
		user.username = obj_in.username
		user.email = obj_in.email
		user.hashed_password = password_hash
		user.is_active = obj_in.is_active
		user.is_superuser = obj_in.is_superuser
		user.full_name = obj_in.full_name
		return self.save(session=session, obj=user)
	
	def get_multi(self, session: Session, skip: int = 0, limit: int = 10) -> Optional[List[User]]:
		select_statement = select(User).order_by(-User.id)
		returned_tuple = session.execute(select_statement)
		row_list = returned_tuple.scalars().all()
		return row_list
	
	def update(
		self, session: Session, obj_in: Union[schemas.UserUpdate, Dict[str, Any]], session_model: User
	) -> Optional[User]:
		if isinstance(obj_in, dict):
			updated_data = obj_in
		else:
			updated_data = obj_in.dict(exclude_unset=True)
		if updated_data["password1"]:
			hashed_password = get_password_hash(updated_data["password1"])
			updated_data["hashed_password"] = hashed_password
			del updated_data["password1"]
			del updated_data["password2"]
		return super().update(
			session=session, session_model=session_model, obj_in=updated_data
		)
	
	def deactivate(
		self,
		*,
		session: Session,
		user: User,
	) -> Optional[User]:
		user.is_active = False
		return self.save(session, user)
	
	# obj_in["is_active"] = False
	# return super().update(session=session, obj_in=obj_in, session_model=db_obj)
	
	def add_user_scope(
		self, session: Session, user: User, scope: models.ScopesEnum
	) -> Optional[User]:
		if scope == models.ScopesEnum.ADMIN:
			scope_object = models.Scope.admin_scope()
		elif scope == models.ScopesEnum.POSTS:
			scope_object = models.Scope.posts_scope()
		elif scope == models.ScopesEnum.ME:
			scope_object = models.Scope.me_scope()
		else:
			scope_object = models.Scope()
		user.scopes.append(scope_object)
		
		return self.save(session, user)
	
	def check_username_exist(self, username: str, session: Session):
		statement = select(self.model.username).where(self.model.username == username)
		existing_username_model = session.execute(statement=statement)
		existing_username = existing_username_model.scalar_one_or_none()
		return existing_username
	
	def check_email_exist(self, email: EmailStr, session: Session):
		statement = select(self.model.email).where(self.model.email == email)
		existing_username_object = session.execute(statement=statement)
		existing_username = existing_username_object.scalar_one_or_none()
		return existing_username
	
	def authenticate_by_email(self, session: Session, email: EmailStr, raw_password: str):
		execution = session.execute(
			select(self.model.email, self.model.hashed_password).where(self.model.email == email)
		)
		user: User = execution.scalar_one_or_none()
		if user and verify_password(plain_password=raw_password, hashed_password=user.hashed_password):
			return user
		else:
			return None
	
	def authenticate(self, session: Session, username: str, raw_password: str) -> User | None:
		user = self.get_user_by_username(username=username, session=session)
		if user and verify_password(plain_password=raw_password, hashed_password=user.hashed_password):
			return user
		else:
			return None
	
	def get_user_by_username(self, session: Session, username: str):
		stmt = select(self.model).where(self.model.username == username)
		db_data = session.execute(stmt)
		return db_data.scalar_one_or_none()
	
	def get_user_by_email(self, session: Session, email: str):
		stmt = select(self.model).where(self.model.email == email)
		db_data = session.execute(stmt)
		return db_data.scalar_one_or_none()


user_dal = UserDAL(User)
