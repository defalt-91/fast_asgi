from core.database.base_db_class import Base
from sqlalchemy.sql.schema import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Text

user_scopes = Table(
	"userscope",
	Base.metadata,
	Column("user_id", Base.id.type, ForeignKey("user.id"), primary_key=True),
	Column("scope_id", Base.id.type, ForeignKey("scope.id"), primary_key=True),
)


class Scope(Base):
	code = Column(String(50), nullable=False, unique=True)
	description = Column(Text)
	
	def __str__(self):
		return self.code
