from typing import Optional
from pydantic import BaseModel
from apps.users.schemas import Author
from pydantic.class_validators import validator


class PostBase(BaseModel):
	title: Optional[str] = None
	body: Optional[str] = None


#  get from user
class PostCreate(PostBase):
	title: str
	body: str


# author_id: int


#  get from user
class PostUpdate(PostBase):
	title: str
	body: str


class PostInDBBase(PostBase):
	id: Optional[str] = None
	author_id: Optional[int] = None
	
	class Config:
		orm_mode = True


# Additional properties stored in DB
class PostInDB(PostInDBBase):
	author_id: int


# Additional properties to return via API
class PostList(PostBase):
	id: int
	author: Author
	
	@validator('author')
	def get_username(cls, v):
		return v.username
	
	class Config:
		orm_mode = True


class PostDetail(PostBase):
	id: int
	author: Author
	
	@validator('author')
	def get_username(cls, v):
		return v.username
	
	class Config:
		orm_mode = True
