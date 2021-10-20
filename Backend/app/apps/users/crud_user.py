from typing import Any, Dict, Optional, Union

from core.base_crud import CRUDBase
from .schemas import UserCreate, UserUpdate
from .models import User
from sqlalchemy.orm.session import Session
from services.password_service import get_password_hash, verify_password
from pydantic import EmailStr


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
	@staticmethod
	def get_user_by_email(db: Session, email: EmailStr) -> Optional[User]:
		return db.query(User).filter(User.email == email).first()
	
	@staticmethod
	def get_user_by_username(db: Session, username: str) -> Optional[User]:
		return db.query(User).filter(User.username == username).first()
	
	def authenticate_by_email(self, db: Session, email: EmailStr, password: str) -> Optional[User]:
		login_user = self.get_user_by_email(db=db, email=email)
		if not login_user:
			return None
		if not verify_password(plain_password=password, hashed_password=login_user.hashed_password):
			return None
		return login_user
	
	def authenticate_by_username(self, db: Session, username: str, password: str) -> Optional[User]:
		login_user = self.get_user_by_username(db=db, username=username)
		if not login_user:
			return None
		if not verify_password(plain_password=password, hashed_password=login_user.hashed_password):
			return None
		return login_user
	
	@staticmethod
	def is_active(user_in: User) -> bool:
		return user_in.is_active
	
	@staticmethod
	def is_superuser(user_in: User) -> bool:
		return user_in.is_superuser
	
	def create_superuser(self, db: Session, obj_in: UserCreate) -> User:
		hashed_password = get_password_hash(obj_in.password1)
		obj = User(
			email=obj_in.email,
			username=obj_in.username,
			hashed_password=hashed_password,
			full_name=obj_in.full_name,
			is_superuser=True,
			is_active=True
		)
		db.add(obj)
		db.commit()
		db.refresh(obj)
		return obj
	
	def create(self, db: Session, *, obj_in: UserCreate) -> User:
		hashed_password = get_password_hash(obj_in.password1)
		obj = User(
			email=obj_in.email,
			username=obj_in.username,
			hashed_password=hashed_password,
			full_name=obj_in.full_name,
			is_active=True
		)
		
		db_obj = obj
		
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj
	
	def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
		if isinstance(obj_in, dict):
			updated_data = obj_in
		else:
			updated_data = obj_in.dict(exclude_unset=True)
		if updated_data["password"]:
			hashed_pass = get_password_hash(updated_data["password"])
			updated_data["hashed_password"] = hashed_pass
			del updated_data["password"]
		return super().update(db=db, db_obj=db_obj, obj_in=updated_data)


# def remove(self, db: Session, *, id: int) -> User:
# 	users = db.query(User).filter(User.id == id).first()
# 	deactive = UserInDB(**users)


user = CRUDUser(User)
