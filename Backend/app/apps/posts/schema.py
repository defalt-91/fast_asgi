from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from pydantic.class_validators import validator


class Author(BaseModel):
    username: Optional[str] = None

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None

    class Config:
        orm_mode = True


#  get from user
class PostCreate(PostBase):
    title: str
    body: str
    author_id: int


#  get from user
class PostUpdate(PostBase):
    title: Optional[str] = None
    body: Optional[str] = None
    author_id: Optional[int] = None


class PostInDBBase(PostBase):
    id: Optional[str] = None
    author_id: Optional[int] = None


# Additional properties stored in DB
class PostInDB(PostInDBBase):
    author_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class PostAuthor(BaseModel):
    id: int = Field(..., ge=1, description="post id ")
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class PostDetail(PostBase):
    id: Optional[int] = None
    author: Optional[PostAuthor] = None

    def name_dict(self):
        return self.dict(include={"author", "id"})


class PostList(PostBase):
    id: int
    author: str

    @validator("author", pre=True)
    def get_username(cls, v):
        return v.username
