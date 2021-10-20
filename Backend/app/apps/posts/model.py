from core.base_crud import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Post(Base):
	title = Column(String, nullable=True, index=True)
	body = Column(String, nullable=True, index=True)
	author_id = Column(Integer, ForeignKey('user.id'))
	author = relationship('User', back_populates="posts")
