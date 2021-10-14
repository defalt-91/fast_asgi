from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	email: Optional[str] = None
	username: Optional[str] = None
	scopes: List[str] = []
	jti: Optional[str] = None


class TokenInDB(BaseModel):
	jwt: str
	user_id: int
	
	class Config:
		orm_mode = True


class TokenCreate(TokenInDB):
	pass


class TokenUpdate(TokenInDB):
	pass
