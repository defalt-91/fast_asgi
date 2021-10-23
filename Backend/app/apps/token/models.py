# from sqlalchemy import Column, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.types import Integer, String
#
# from core.database.base_db_class import Base
#
#
# class Token(Base):
# 	id = Column(
# 		Integer, autoincrement=True, unique=True,
# 		nullable=False, primary_key=True, index=True
# 		)
# 	jwt = Column(String, nullable=False)
# 	user_id = Column(Integer, ForeignKey("user.id"))
# 	user = relationship('User', back_populates="tokens")
