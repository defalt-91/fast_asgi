from pydantic import BaseModel
from typing import List, Optional


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	email: Optional[str] = None
	scopes: List[str] = []
	jti: Optional[str] = None
