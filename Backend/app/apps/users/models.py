from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database.registry import NameAndIDMixin, mapper_registry
from apps.scopes.models import UserScopes
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.ext.compiler import compiles


class utcnow(FunctionElement):
	type = DateTime()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
	return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@mapper_registry.mapped
class User(NameAndIDMixin):
	full_name = Column(String(length=255), unique=False, index=True, nullable=True)
	email = Column(String(length=255), unique=True, index=True, nullable=True)
	username = Column(String(length=255), unique=True, index=True, nullable=False)
	hashed_password = Column(String(length=255), nullable=False)
	is_active = Column(Boolean(), default=True, nullable=False, index=True)
	is_superuser = Column(Boolean(), default=False, nullable=False, index=True)
	date_joined = Column(DateTime(timezone=True), server_default=utcnow(), index=True)
	is_staff = Column(Boolean, default=False, doc="if true user can login to admin app")
	profile = relationship(
		"Profile",
		back_populates="user",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all, delete",
		passive_deletes=True,
		uselist=False,
	)
	posts = relationship(
		"Post",
		back_populates="author",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all, delete",
		passive_deletes=True,
		order_by="desc(Post.created_at)",
	)
	scopes = relationship(
		"Scope",
		secondary=UserScopes.__tablename__,
		back_populates="users",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all, delete",
		passive_deletes=True,
		# one-to-one Parent.child
		# single_parent=True,
	)
	tokens = relationship(
		"Token",
		back_populates="user",
		order_by="desc(Token.created_at)",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all, delete",
		passive_deletes=True,
	)
	
	def __str__(self):
		return f"{self.__class__}({self.username} , {self.email}, {self.scopes})"
	
	def __repr__(self):
		return self.__str__()
	
	@property
	def is_authenticated(self) -> bool:
		return self.is_active
	
	@property
	def display_name(self) -> str:
		return f"{self.full_name}"


@mapper_registry.mapped
class Profile(NameAndIDMixin):
	user_id = Column(ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False)
	user = relationship(
		"User",
		back_populates="profile",
		single_parent=True,
		cascade="all, delete, delete-orphan",
	)
