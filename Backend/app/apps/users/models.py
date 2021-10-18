from core.database.base_db_class import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, Boolean, Integer
from sqlalchemy.orm import relationship


class User(Base):
	full_name = Column(String, unique=False, index=True, nullable=True)
	email = Column(String, unique=True, index=True, nullable=True)
	username = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False, )
	is_active = Column(Boolean(), default=True, nullable=False)
	is_superuser = Column(Boolean(), default=False, nullable=False)
# user = relationship('User', back_populates="user")

# items = relationship("Item", back_populates="owner")
