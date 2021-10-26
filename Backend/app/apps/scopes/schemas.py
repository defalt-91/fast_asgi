from typing import Optional
from pydantic import BaseModel


class ScopeBase(BaseModel):
	code: Optional[str] = None
	description: Optional[str] = None


class ScopeIn(ScopeBase):
	code: str
	description: str


class ScopeOut(ScopeBase):
	id: int
	code: str
	description: str


class UserScopesBase(BaseModel):
	user_id: Optional[int] = None
	scope_id: Optional[int] = None


class UserScopesIn(UserScopesBase):
	user_id: int
	scope_id: int


class UserScopesOut(UserScopesBase):
	id: int
	user_id: int
	scope_id: int
