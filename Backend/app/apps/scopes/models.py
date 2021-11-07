import sqlalchemy.orm as sql_orm
import core.database.registry as core_reg
import core.database.session as core_ses
import enum
import sqlalchemy.sql.sqltypes as sql_type
import sqlalchemy.sql.schema as sql_schema
import sqlalchemy.sql.expression as sql_exp


@enum.unique
class ScopesEnum(enum.IntEnum):
	ME = 1
	POSTS = 2
	ADMIN = 3


@core_reg.mapper_registry.mapped
class UserScopes:
	__tablename__ = "userscopes"
	user_id = sql_schema.Column(
		# A database level ON DELETE cascade is configured effectively on the many-to-one side of the relationship
		sql_schema.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, nullable=False
	)
	scope_id = sql_schema.Column(
		# A database level ON DELETE cascade is configured effectively on the many-to-one side of the relationship
		sql_schema.ForeignKey("scope.id", ondelete="CASCADE"), primary_key=True, nullable=False
	)
	
	def __repr__(self):
		return f"<{self.__class__.__name__}"
	
	def __str__(self):
		return self.__repr__()


@core_reg.mapper_registry.mapped
class Scope(core_reg.NameAndIDMixin):
	code = sql_schema.Column(sql_type.String(50), nullable=False, unique=True)
	description = sql_schema.Column(sql_type.String(255))
	users = sql_orm.relationship(
		"User",
		secondary=UserScopes.__tablename__,
		back_populates="scopes",
		# passive_deletes=True,
		# cascade="all, delete",
	)
	
	def __str__(self):
		return self.code
	
	def __repr__(self):
		return self.code
	
	@staticmethod
	def admin_scope():
		with core_ses.SessionFactory() as session:
			statement = sql_exp.select(Scope).where(Scope.id == ScopesEnum.ADMIN.value)
			returned_tuple = session.execute(statement)
			row = returned_tuple.scalar_one_or_none()
		return row
	
	@staticmethod
	def posts_scope():
		with core_ses.SessionFactory.begin() as session:
			statement = sql_exp.select(Scope).where(Scope.id == ScopesEnum.POSTS.value)
			returned_tuple = session.execute(statement)
			row = returned_tuple.scalar_one_or_none()
		return row
	
	@staticmethod
	def me_scope():
		with core_ses.SessionFactory.begin() as session:
			statement = sql_exp.select(Scope).where(Scope.id == ScopesEnum.ME.value)
			returned_tuple = session.execute(statement)
			row = returned_tuple.scalar_one_or_none()
		return row
