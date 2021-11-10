import uuid
import sqlalchemy.dialects.postgresql.base as pg_base
import sqlalchemy.types as sql_types
import sqlalchemy.schema as sql_schema
import sqlalchemy.orm as sql_rel
import core.database.registry as core_reg


@core_reg.mapper_registry.mapped
class Token:
	__tablename__ = 'token'
	jti = sql_schema.Column(pg_base.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
	created_at = sql_schema.Column(sql_types.TIMESTAMP(timezone=True), server_default=core_reg.utcnow(), index=True)
	expire_at = sql_schema.Column(sql_types.TIMESTAMP(timezone=True), nullable=False, index=True)
	jwt = sql_schema.Column(sql_types.String(455), nullable=True)
	token_type = sql_schema.Column(sql_types.String(50), nullable=False)
	user_id = sql_schema.Column(
		sql_types.Integer, sql_schema.ForeignKey("user.id", ondelete="CASCADE"),
		nullable=False
	)
	user = sql_rel.relationship("User", back_populates="tokens", order_by="desc(Token.created_at)")
	
	def __repr__(self):
		return f"<{self.__class__.__name__}, id={self.jti}>"
	
	def __str__(self):
		return self.__repr__()
	
	__mapper_args__ = {"always_refresh": True}


class BlackList:
	pass
