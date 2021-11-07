import gzip
import datetime as dt
import pathlib as pt
import typing
import re
import pydantic.class_validators as py_validators
import pydantic.main as py_main
import pydantic.networks as py_net
import apps.scopes.schemas as s_schema


pattern2 = r"[A-Za-z0-9@#$%^&+=]{8,}"
pattern = "^.*(?=.{7,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
DEFAULT_PASSWORD_LIST_PATH = pt.Path(__file__).resolve().parent / "common-passwords.txt.gz"
# reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
reg = "^(?=.*[a-z])(?=.*\d)[A-Za-z\d@$!#%*?&][A-Za-z\d@$!#%*?&]{7,20}$"

common_passwords: {}
with gzip.open(DEFAULT_PASSWORD_LIST_PATH, "rt", encoding="utf-8") as f:
	common_passwords = {x.strip() for x in f}


# Shared properties
class UserBase(py_main.BaseModel):
	username: typing.Optional[str] = None
	email: typing.Optional[py_net.EmailStr] = None
	full_name: typing.Optional[str] = None
	is_active: typing.Optional[bool] = True
	is_superuser: typing.Optional[bool] = False
	is_staff: typing.Optional[bool] = False
	
	class Config:
		orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserBase):
	username: str
	password1: str
	password2: str
	
	@py_validators.validator("password2")
	def password_validators(cls, v, values):
		if "password1" in values and v != values["password1"]:
			raise ValueError("passwords do not match")
		if len(v) < 7:
			raise ValueError("password need to be more than 8 characters")
		if v.lower().strip() in common_passwords:
			"""The password is rejected if it occurs in a provided list of passwords,"""
			raise ValueError("This password in to common, use a better password")
		
		if v.isdigit():
			"""Validate whether the password is alphanumeric."""
			raise ValueError("This password is entirely numeric.")
		
		# result = re.fullmatch(pattern2, v)
		result = re.search(reg, v)
		if not result:
			raise ValueError(
				"Password must be at least 8 characters and includes numbers and words "
			)
		return v
	
	@py_validators.validator("username")
	def username_check(cls, v, values):
		if not v.isalnum:
			raise ValueError("username must be alphanumeric")
		return v


class UserInDBBase(UserBase):
	id: typing.Optional[int] = None
	date_joined: typing.Optional[dt.datetime] = None
	is_staff: typing.Optional[bool] = False
	scopes: typing.List[s_schema.ScopeOut]


# @validator("scopes", pre=True)
# def list_of_scopes(cls, v):
#     return [scope for scope in v]


# Additional properties stored in DB
class UserInDB(UserInDBBase):
	hashed_password: str
	username: str


# Additional properties to return via API
class User(UserInDBBase):
	id: typing.Optional[int] = None
	username: typing.Optional[str] = None
	full_name: typing.Optional[str] = None
	
	class Config:
		orm_mode = True


class UserDeactivate(UserInDBBase):
	is_active: bool = False


class Msg(py_main.BaseModel):
	msg: str


class Password(py_main.BaseModel):
	password1: typing.Optional[str] = None
	password2: typing.Optional[str] = None
	
	@py_validators.root_validator()
	def password_validators(cls, values):
		pwd1, pwd2 = values.get("password1"), values.get("password2")
		if (pwd1 and pwd2) and not (pwd2 == pwd1):
			raise ValueError("Passwords do not match")
		if len(pwd1) < 7:
			raise ValueError("password need to be more than 8 characters")
		if pwd1.lower().strip() in common_passwords:
			"""The password is rejected if it occurs in a provided list of passwords,"""
			raise ValueError("This password in to common, use a better password")
		
		if pwd1.isdigit():
			"""Validate whether the password is alphanumeric."""
			raise ValueError("This password is entirely digit.")
		result = re.search(reg, pwd1)
		if not result:
			raise ValueError(
				"Password must be at least 8 characters and includes numbers and words "
			)
		return values


# Properties to receive via API on update
class UserUpdate(Password):
	username: typing.Optional[str] = None
	email: typing.Optional[py_net.EmailStr] = None
	full_name: typing.Optional[str] = None
	
	class Config:
		orm_mode = True
