import apps.scopes.models as sc_model
import sqlalchemy.sql.functions as sql_func
import sqlalchemy.ext.compiler as sql_comp
import sqlalchemy.types as sql_types
import sqlalchemy.schema as sql_schema
import sqlalchemy.orm as sql_rel
import core.database.registry as core_reg


class utcnow(sql_func.FunctionElement):
	type = sql_types.DateTime()


@sql_comp.compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
	return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@core_reg.mapper_registry.mapped
class User(core_reg.NameAndIDMixin):
	full_name = sql_schema.Column(sql_types.String(length=255), unique=False, index=True, nullable=True)
	email = sql_schema.Column(sql_types.String(length=255), unique=True, index=True, nullable=True)
	username = sql_schema.Column(sql_types.String(length=255), unique=True, index=True, nullable=False)
	hashed_password = sql_schema.Column(sql_types.String(length=255), nullable=False)
	is_active = sql_schema.Column(sql_types.Boolean(), default=True, nullable=False, index=True)
	is_superuser = sql_schema.Column(sql_types.Boolean(), default=False, nullable=False, index=True)
	date_joined = sql_schema.Column(sql_types.DateTime(timezone=True), server_default=utcnow(), index=True)
	is_staff = sql_schema.Column(sql_types.Boolean, default=False, doc="if true user can login to admin app")
	profile = sql_rel.relationship(
		"Profile",
		back_populates="user",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all , delete",
		passive_deletes=True,
		uselist=False,
	)
	posts = sql_rel.relationship(
		"Post",
		back_populates="author",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all , delete",
		passive_deletes=True,
		order_by="desc(Post.created_at)",
	)
	scopes = sql_rel.relationship(
		"Scope",
		secondary=sc_model.UserScopes.__tablename__,
		back_populates="users",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all , delete",
		passive_deletes=True,
		# one-to-one Parent.child
		# single_parent=True,
	)
	tokens = sql_rel.relationship(
		"Token",
		back_populates="user",
		order_by="desc(Token.created_at)",
		# FOR DELETING RELATIONAL OBJECTS IN DB NOT IN ORM, NEED on_delete="all,delete" ON THE OTHER SIDE
		cascade="all , delete",
		passive_deletes=True,
	)
	
	def __str__(self):
		return f"{self.__class__}({self.username} , {self.email}, {self.scopes})"
	
	def __repr__(self):
		return self.__str__()
	
	@property
	def is_admin(self) -> bool:
		return self.is_superuser
	
	@property
	def display_name(self) -> str:
		return f"{self.full_name}"


@core_reg.mapper_registry.mapped
class Profile(core_reg.NameAndIDMixin):
	user_id = sql_schema.Column(sql_schema.ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False)
	user = sql_rel.relationship(
		"User",
		back_populates="profile",
		single_parent=True,
		cascade="all, delete, delete-orphan",
	)
