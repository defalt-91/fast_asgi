from sqlalchemy.orm import registry, declarative_mixin, declared_attr
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, Integer
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.ext.compiler import compiles


class utcnow(FunctionElement):
    type = DateTime()


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


mapper_registry = registry(_bind=True)


@declarative_mixin
class NameAndIDMixin:
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        autoincrement=True,
        unique=True,
    )

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        return f"<{self.__class__.__name__}, id={self.id}>"

    def __str__(self):
        return self.__repr__()

    __mapper_args__ = {"always_refresh": True}


@declarative_mixin
class DateMixin:
    created_at = Column(DateTime(timezone=False), server_default=utcnow(), index=True)
    updated_at = Column(DateTime(timezone=False), onupdate=utcnow(), index=True)


@declarative_mixin
class RefAuthorMixin:
    @declared_attr
    def author_id(cls):
        return Column(
            "author_id", ForeignKey("user.id", ondelete="CASCADE"), nullable=False
        )

    @declared_attr
    def author(cls):
        return relationship("User", back_populates="posts")


# @declarative_mixin
# class RefTargetMixin:
# 	@declared_attr
# 	def target_id(cls):
# 		return Column('target_id', ForeignKey('target.id'))
#
# 	@declared_attr
# 	def target(cls):
# 		return relationship(
# 			Target,
# 			primaryjoin=lambda: Target.id == cls.target_id
# 		)
