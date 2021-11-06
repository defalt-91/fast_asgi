from enum import Enum
from typing import Any, List, Optional, Sequence
from pydantic import BaseModel, validator

from apps.scopes.models import ScopesEnum
from services.scopes import ScopeTypes


class ScopeBase(BaseModel):
	code: Optional[ScopeTypes] = None
	description: Optional[str] = None
	
	class Config:
		orm_mode = True


class ScopeIn(ScopeBase):
	code: ScopeTypes
	description: str


class ScopeOut(ScopeBase):
	id: int
	code: ScopeTypes
	description: str


class ScopeUser(BaseModel):
	username: str
	id: int
	email: Any
	
	class Config:
		orm_mode = True


class ScopeOutWithUsers(ScopeOut):
	users: List[ScopeUser]
