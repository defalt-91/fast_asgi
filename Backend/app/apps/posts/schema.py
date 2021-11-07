import datetime
import typing
import pydantic.fields as py_field
import pydantic.main as py_main
import pydantic.class_validators as py_validators


class Author(py_main.BaseModel):
	username: typing.Optional[str] = None
	
	class Config:
		orm_mode = True


class PostBase(py_main.BaseModel):
	title: typing.Optional[str] = None
	body: typing.Optional[str] = None
	
	class Config:
		orm_mode = True


#  get from user
class PostCreate(PostBase):
	title: str
	body: str
	author_id: int


#  get from user
class PostUpdate(PostBase):
	title: typing.Optional[str] = None
	body: typing.Optional[str] = None
	author_id: typing.Optional[int] = None


class PostInDBBase(PostBase):
	id: typing.Optional[str] = None
	author_id: typing.Optional[int] = None


# Additional properties stored in DB
class PostInDB(PostInDBBase):
	author_id: int
	created_at: typing.Optional[datetime.datetime] = None
	updated_at: typing.Optional[datetime.datetime] = None
	
	class Config:
		orm_mode = True


class PostAuthor(py_main.BaseModel):
	id: int = py_field.Field(..., ge=1, description="post id ")
	username: str
	full_name: typing.Optional[str] = None
	email: typing.Optional[str] = None
	
	class Config:
		orm_mode = True


# Additional properties to return via API
class PostDetail(PostBase):
	id: typing.Optional[int] = None
	author: typing.Optional[PostAuthor] = None
	
	def name_dict(self):
		return self.dict(include={"author", "id"})


class PostList(PostBase):
	id: int
	author: str
	
	@py_validators.validator("author", pre=True)
	def get_username(cls, v):
		return v.username
