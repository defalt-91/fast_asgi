from enum import Enum
from typing import Any, List, Optional, Sequence
from pydantic import BaseModel, validator

from apps.scopes.models import ScopesEnum


class ScopeBase(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class ScopeIn(ScopeBase):
    code: str
    description: str


class ScopeOut(ScopeBase):
    id: int
    code: str
    description: str


class ScopeUser(BaseModel):
    username: str
    id: int
    email: Any

    class Config:
        orm_mode = True


class ScopeOutWithUsers(ScopeOut):
    users: List[ScopeUser]

