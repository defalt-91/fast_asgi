from services.base_dal import BaseDAL
from . import schemas
from .models import User
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import Any, Dict, List, Optional, Union
from pydantic import EmailStr
from services.password_service import get_password_hash, verify_password
from fastapi import Depends

from ..scopes.models import Scope, ScopesEnum, UserScopes


class UserDAL(BaseDAL[User, schemas.UserCreate, schemas.UserUpdate]):
    # def __init__(self, *args, **kwargs):
    #     self.session: Session = get_session()
    #     super().__init__(*args, **kwargs)

    def create(self, session: Session, obj_in: schemas.UserCreate) -> Optional[User]:
        password_hash = get_password_hash(obj_in.password2)
        user: User = User()
        user.username = obj_in.username
        user.email = obj_in.email
        user.hashed_password = password_hash
        user.is_active = obj_in.is_active
        user.is_superuser = obj_in.is_superuser
        user.full_name = obj_in.full_name
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def get_multi(
        self, session: Session, skip: int = 0, limit: int = 10
    ) -> Optional[List[User]]:
        select_statement = select(User).order_by(-User.id)
        returned_tuple = session.execute(select_statement)
        row_list = returned_tuple.scalars().all()
        return row_list

    def update(
        self,
        session: Session,
        obj_in: Union[schemas.UserUpdate, Dict[str, Any]],
        session_model: User,
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

    @staticmethod
    def deactivate(
        *,
        session: Session,
        user: User,
    ) -> Optional[User]:
        user.is_active = False
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
        # obj_in["is_active"] = False
        # return super().update(session=session, obj_in=obj_in, session_model=db_obj)

    @staticmethod
    def add_user_scope(
        session: Session, user: User, scope: ScopesEnum
    ) -> Optional[User]:
        if scope == ScopesEnum.ADMIN:
            scope_object = Scope.admin_scope()
        elif scope == ScopesEnum.POSTS:
            scope_object = Scope.posts_scope()
        elif scope == ScopesEnum.ME:
            scope_object = Scope.me_scope()
        else:
            scope_object = Scope()
        user.scopes.append(scope_object)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def get_user_by_email(self, session: Session, email: Union[str,EmailStr]) -> Optional[User]:
        statement = select(self.model).where(self.model.email == email)
        return session.execute(statement).scalar_one_or_none()

    def get_user_by_username(self, session: Session, username: str) -> Optional[User]:
        statement = select(self.model).where(self.model.username == username)
        return session.execute(statement).scalar_one_or_none()

    def check_username_exist(self, username: str, session: Session):
        statement = select(self.model.username).where(self.model.username == username)
        existing_username = session.execute(statement=statement).scalar_one_or_none()
        return existing_username

    def check_email_exist(self, email: EmailStr, session: Session):
        statement = select(self.model.email).where(self.model.email == email)
        existing_username = session.execute(statement=statement).scalar_one_or_none()
        return existing_username

    def authenticate_by_email(
        self, session: Session, email: EmailStr, raw_password: str
    ):
        execution = session.execute(
            select(self.model.email, self.model.hashed_password).where(
                self.model.email == email
            )
        )
        user: User = execution.scalar_one_or_none()
        if user:
            if verify_password(
                plain_password=raw_password, hashed_password=user.hashed_password
            ):
                return user
            else:
                return None
        else:
            return None

    def authenticate_by_username(
        self, session: Session, username: str, raw_password: str
    ) -> Optional[Any]:
        execution = session.execute(
            select(self.model).where(self.model.username == username)
        )
        user = execution.scalar_one_or_none()
        if user:
            if verify_password(
                plain_password=raw_password, hashed_password=user.hashed_password
            ):
                return user
            else:
                return None
        else:
            return None

    @staticmethod
    def is_active(user_in: User) -> bool:
        return user_in.is_active

    @staticmethod
    def is_superuser(user_in: User) -> bool:
        return user_in.is_superuser


user_dal: UserDAL = UserDAL(User)
