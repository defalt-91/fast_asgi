from apps.scopes.models import user_scopes
from core.database.base_db_class import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String,  Boolean
from sqlalchemy.orm import relationship


class User(Base):
	full_name = Column(String, unique=False, index=True, nullable=True)
	email = Column(String, unique=True, index=True, nullable=True)
	username = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False, )
	is_active = Column(Boolean(), default=True, nullable=False)
	is_superuser = Column(Boolean(), default=False, nullable=False)
	posts = relationship("Post", back_populates="author")
	scopes = relationship("Scope", secondary=user_scopes)
	
	def __str__(self):
		return self.email
	
	@property
	def is_authenticated(self) -> bool:
		return self.is_active
	
	@property
	def display_name(self) -> str:
		return f"{self.first_name} {self.last_name}"


# def set_password(self, password) -> None:
# 	salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
# 	password_hash = hashlib.pbkdf2_hmac(
# 		"sha512", password.encode("utf-8"), salt, 100000
# 	)
# 	password_hash = binascii.hexlify(password_hash)
# 	self.password = (salt + password_hash).decode("ascii")
#
# def check_password(self, password) -> bool:
# 	salt = self.password[:64]
# 	stored_password = self.password[64:]
# 	password_hash = hashlib.pbkdf2_hmac(
# 		"sha512", password.encode("utf-8"), salt.encode("ascii"), 100000
# 	)
# 	password_hash = binascii.hexlify(password_hash).decode("ascii")  # type: ignore
# 	return password_hash == stored_password


# user = relationship('User', back_populates="user")

