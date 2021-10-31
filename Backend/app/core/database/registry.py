from sqlalchemy.orm import backref, registry, declarative_mixin, declared_attr
from sqlalchemy import func, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

mapper_registry = registry(_bind=True)


# @declarative_mixin
# class TimestampMixin:
# 	created_at = Column(DateTime, default=func.now()) @ declarative_mixin


@declarative_mixin
class NameAndIDMixin:
	id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, unique=True, index=True)
	
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()
	
	def __repr__(self):
		return f"<{self.__class__.__name__}, id={self.id}>"
	
	def __str__(self):
		return self.__repr__()
	
	__mapper_args__ = {'always_refresh': True}
	

@declarative_mixin
class RefAuthorMixin:
	@declared_attr
	def author_id(cls):
		return Column('author_id', ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
	
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
