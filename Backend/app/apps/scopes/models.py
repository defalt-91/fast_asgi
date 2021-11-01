from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Text
from sqlalchemy.orm import relationship
from core.database.registry import NameAndIDMixin, mapper_registry
from core.database.session import SessionLocal
from sqlalchemy import select
from enum import unique, IntEnum


@unique
class ScopesEnum(IntEnum):
    ME = 1
    POSTS = 2
    ADMIN = 3


@mapper_registry.mapped
class UserScopes:
    __tablename__ = "userscopes"
    user_id = Column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    scope_id = Column(
        ForeignKey("scope.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}"

    def __str__(self):
        return self.__repr__()


@mapper_registry.mapped
class Scope(NameAndIDMixin):
    code = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    users = relationship(
        "User",
        secondary=UserScopes.__tablename__,
        back_populates="scopes",
        passive_deletes=True,
        cascade="all, delete",
    )

    def __str__(self):
        return self.code

    def __repr__(self):
        return self.code

    @staticmethod
    def admin_scope():
        with SessionLocal() as session:
            statement = select(Scope).where(Scope.id == ScopesEnum.ADMIN.value)
            returned_tuple = session.execute(statement)
            row = returned_tuple.scalar_one_or_none()
        return row

    @staticmethod
    def posts_scope():
        with SessionLocal.begin() as session:
            statement = select(Scope).where(Scope.id == ScopesEnum.POSTS.value)
            returned_tuple = session.execute(statement)
            row = returned_tuple.scalar_one_or_none()
        return row

    @staticmethod
    def me_scope():
        with SessionLocal.begin() as session:
            statement = select(Scope).where(Scope.id == ScopesEnum.ME.value)
            returned_tuple = session.execute(statement)
            row = returned_tuple.scalar_one_or_none()
        return row
