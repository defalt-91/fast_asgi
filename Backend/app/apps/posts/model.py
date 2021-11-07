import sqlalchemy.types as sql_types
import sqlalchemy.schema as sql_schema
import core.database.registry as core_reg


@core_reg.mapper_registry.mapped
class Post(core_reg.NameAndIDMixin, core_reg.RefAuthorMixin, core_reg.DateMixin):
	title = sql_schema.Column(sql_types.String(255), nullable=True, index=True)
	body = sql_schema.Column(sql_types.String(255), nullable=True, index=True)
	
	def __repr__(self):
		return f"{self.title}"
