from sqlalchemy import Column, String
from core.database.registry import (
    DateMixin,
    NameAndIDMixin,
    mapper_registry,
    RefAuthorMixin,
)


@mapper_registry.mapped
class Post(NameAndIDMixin, RefAuthorMixin, DateMixin):
    title = Column(String(255), nullable=True, index=True)
    body = Column(String(255), nullable=True, index=True)

    def __repr__(self):
        return f"{self.title}"
