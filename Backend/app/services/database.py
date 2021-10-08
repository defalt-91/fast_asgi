from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker, Session
from typing import Any
from ..configurations.settings_json import DATABASE_USER, DATABASE_URL


@as_declarative
class Base:
	id: Any
	__name__: str
	
	# Generate __tablename__ automatically
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()


engine = create_engine(url=DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
