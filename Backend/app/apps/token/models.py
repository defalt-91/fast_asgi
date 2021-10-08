# from core.database.base_db_class import Base
# from sqlalchemy.sql.sqltypes import Integer, String, Boolean
# from sqlalchemy.sql.schema import Column

# if TYPE_CHECKING:
#     from .item import Item  # noqa: F401
#
#
# class Token(Base):
# 	id = Column(Integer, autoincrement=True, nullable=False, primary_key=True, unique=True, index=True)
#

"""
{
  "iss": "https://YOUR_DOMAIN/",
  "sub": "auth0|123456",
  "aud": [
    "my-api-identifier",
    "https://YOUR_DOMAIN/userinfo"
  ],
  "azp": "YOUR_CLIENT_ID",
  "exp": 1489179954,
  "iat": 1489143954,
  "scope": "openid profile email address phone read:appointments"
}
"""
