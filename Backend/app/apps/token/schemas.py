import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Literal, Optional, Sequence, Union

import pydantic
from apps.token.models import TokenTypes
from core.base_settings import settings
from services.scopes import ScopeTypes


class Token(pydantic.BaseModel):
	access_token: str
	token_type: str


class TokenData(pydantic.BaseModel):
	email: Optional[str] = None
	username: Optional[str] = None
	scopes: List[str] = []
	jti: Optional[str] = None


class TokenInDBBase(pydantic.BaseModel):
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


# a=Token(token_type='',access_token='')
# b=a.json()
# Token.json_encoder(b)
# Token.schema(b)


class TokenScopesTypes(str, Enum):
	ADMIN = "admin"
	ME = "me"
	POSTS = "posts"


class JwtClaims(pydantic.BaseModel):
	"""model class for creating jwt claims"""
	
	# typ
	sub: str
	iss: Optional[str] = settings.JWT_ISSUER
	exp: Optional[timedelta] = None
	iat: Optional[datetime] = datetime.utcnow()
	aud: Optional[pydantic.HttpUrl] = pydantic.Field(default_factory=lambda: settings.FRONTEND_ORIGIN)
	nbf: Optional[int] = None


class AccessTokenJwtClaims(JwtClaims):
	scopes: List[ScopeTypes] = []
	exp: Optional[timedelta] = pydantic.Field(
		default_factory=lambda: datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
	)


class RefreshTokenJwtClasims(JwtClaims):
	jti: Optional[str] = None
# @pydantic.root_validator(pre=True)
# def create_uuid4(cls, values):
# 	values['jti'] =str( uuid.uuid4().urn)
# 	return values
