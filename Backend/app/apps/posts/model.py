from sqlalchemy import Column, String
from core.database.registry import NameAndIDMixin, mapper_registry, RefAuthorMixin


@mapper_registry.mapped
class Post(NameAndIDMixin, RefAuthorMixin):
	title = Column(String, nullable=True, index=True)
	body = Column(String, nullable=True, index=True)
	
	def __repr__(self):
		return f"{self.title}"
