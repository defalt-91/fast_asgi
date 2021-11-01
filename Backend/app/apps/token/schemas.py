from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

from apps.token.models import TokenTypes


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    scopes: List[str] = []
    jti: Optional[str] = None


class TokenInDBBase(BaseModel):
    jwt: str
    user_id: int
    token_type: TokenTypes


class TokenInDB(TokenInDBBase):
    created_at: datetime

    class Config:
        orm_mode = True


class TokenCreate(TokenInDBBase):
    pass


class TokenUpdate(TokenInDBBase):
    pass
