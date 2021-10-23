from sqlalchemy.ext.declarative import as_declarative, declared_attr
from typing import Any
from sqlalchemy import Column, Integer


@as_declarative()
class Base:
	id: int = Column(Integer, autoincrement=True, unique=True, nullable=False, primary_key=True)
	__name__: str
	
	# Generate __tablename__ automatically
	@declared_attr
	def __tablename__(cls) -> str:
		return cls.__name__.lower()
