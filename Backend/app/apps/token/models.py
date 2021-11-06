import enum
import uuid

from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from core.database.registry import NameAndIDMixin, mapper_registry, utcnow


class TokenTypes(str, enum.Enum):
	ACCESS_TOKEN = "access_token"
	REFRESH_TOKEN = "refresh_token"


@mapper_registry.mapped
class Token:
	__tablename__ = 'token'
	uid = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
	created_at = Column(DateTime(timezone=False), server_default=utcnow(), index=True)
	jwt = Column(String(455), nullable=True)
	token_type = Column(String(50), nullable=False, default=TokenTypes.ACCESS_TOKEN)
	user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
	user = relationship(
		"User", back_populates="tokens", order_by="desc(Token.created_at)"
	)
	
	def __repr__(self):
		return f"<{self.__class__.__name__}, id={self.id}>"
	
	def __str__(self):
		return self.__repr__()
	
	__mapper_args__ = {"always_refresh": True}


class BlackList:
	pass
