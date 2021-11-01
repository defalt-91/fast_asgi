import enum

from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Enum

from core.database.registry import NameAndIDMixin, mapper_registry, utcnow


class TokenTypes(str, enum.Enum):
    ACCESS_TOKEN = "access_token"
    REFRESH_TOKEN = "refresh_token"


@mapper_registry.mapped
class Token(NameAndIDMixin):
    __tablename__ = "token"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        autoincrement=True,
        unique=True,
    )
    created_at = Column(DateTime(timezone=False), server_default=utcnow(), index=True)
    jwt = Column(String(455), nullable=True)
    token_type = Column(String(50), nullable=False, default=TokenTypes.ACCESS_TOKEN)
    user_id = Column(Integer, ForeignKey("user.id"))
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
