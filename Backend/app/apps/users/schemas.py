from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
	username: str
	email: Optional[str] = None
	full_name: Optional[str] = None
	is_active: Optional[bool] = None


class UserInDB(User):
	hashed_password: str
