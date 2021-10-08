from core.database.base_db_class import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, Boolean, Integer


class User(Base):
	id = Column(Integer, autoincrement=True, nullable=False, primary_key=True, unique=True, index=True)
	full_name = Column(String, unique=False, index=True, nullable=True)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False, )
	is_active = Column(Boolean(), default=True, nullable=False)
	is_superuser = Column(Boolean(), default=False, nullable=False)
# items = relationship("Item", back_populates="owner")
