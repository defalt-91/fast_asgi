import gzip
from operator import setitem
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
import re

from pydantic import BaseModel, EmailStr, validator, root_validator

from apps.scopes.models import Scope
from apps.scopes.schemas import ScopeOut
from services import errors


pattern2 = r"[A-Za-z0-9@#$%^&+=]{8,}"
pattern = "^.*(?=.{7,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / "common-passwords.txt.gz"
# reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
reg = "^(?=.*[a-z])(?=.*\d)[A-Za-z\d@$!#%*?&][A-Za-z\d@$!#%*?&]{7,20}$"

common_passwords: {}
with gzip.open(DEFAULT_PASSWORD_LIST_PATH, "rt", encoding="utf-8") as f:
    common_passwords = {x.strip() for x in f}


# Shared properties
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    password1: str
    password2: str

    @validator("password2")
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

    @validator("username")
    def username_check(cls, v, values):
        if not v.isalnum:
            raise ValueError("username must be alphanumeric")
        return v


class UserInDBBase(UserBase):
    id: Optional[int] = None
    scopes: List[ScopeOut]

    # @validator("scopes", pre=True)
    # def list_of_scopes(cls, v):
    #     return [scope for scope in v]


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
    username: str


# Additional properties to return via API
class User(UserInDBBase):
    id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    # scopes: List[Dict[str, str]]
    #
    # @validator("scopes", pre=True)
    # def list_of_scopes(cls, v):
    #     mylist = []
    #     for i in v:
    #         mydict = dict()
    #         setitem(mydict, str(i.code), str(i.description))
    #         mylist.append(mydict)
    #     return mylist

    class Config:
        orm_mode = True


class UserProfile:
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    id: Optional[int] = None


class UserDeactivate(UserInDBBase):
    is_active: bool = False


class Msg(BaseModel):
    msg: str


class Author(BaseModel):
    username: Optional[str] = None

    class Config:
        orm_mode = True


class Password(BaseModel):
    password1: Optional[str] = None
    password2: Optional[str] = None

    @root_validator()
    def password_validators(cls, values):
        pwd1, pwd2 = values.get("password1"), values.get("password2")
        if pwd1 and pwd2 and not pwd2 == pwd1:
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
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

    class Config:
        orm_mode = True
