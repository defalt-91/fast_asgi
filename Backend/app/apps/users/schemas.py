from typing import Optional

from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
	# username: Optional[str]
	email: Optional[EmailStr] = None
	full_name: Optional[str] = None
	is_active: Optional[bool] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
	email: EmailStr
	raw_password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
	raw_password: Optional[str] = None


class UserInDBBase(UserBase):
	id: Optional[int] = None
	
	class Config:
		orm_mode = True


# Additional properties stored in DB
class UserInDB(UserInDBBase):
	hashed_password: str


# Additional properties to return via API
class User(UserInDBBase):
	id: Optional[int] = None
	email: Optional[EmailStr] = None
	full_name: Optional[str] = None
	# is_active: Optional[bool] = None
