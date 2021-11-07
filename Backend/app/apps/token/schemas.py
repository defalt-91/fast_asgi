import uuid
import datetime as dt
import enum
import typing
import pydantic.main as py_main
import services.scopes as scope_service
import core.base_settings as b_settings
import pydantic.class_validators as py_validators
import pydantic.fields as py_fields
import pydantic.networks as py_net


settings = b_settings.get_settings()


class TokenTypes(str, enum.Enum):
	ACCESS_TOKEN = "access_token"
	REFRESH_TOKEN = "refresh_token"


class Token(py_main.BaseModel):
	access_token: str
	token_type: str


class TokenData(py_main.BaseModel):
	email: typing.Optional[str] = None
	username: typing.Optional[str] = None
	scopes: typing.List[str] = []
	jti: typing.Optional[uuid.UUID] = None


class TokenInDBBase(py_main.BaseModel):
	jwt: str
	user_id: int
	token_type: TokenTypes
	expire_at: dt.datetime


class RefreshTokenInDB(TokenInDBBase):
	created_at: dt.datetime
	expire_at: dt.datetime
	jti: uuid.UUID
	
	class Config:
		orm_mode = True


class RefreshTokenCreate(TokenInDBBase):
	jti: uuid.UUID


class TokenUpdate(TokenInDBBase):
	pass


# a=Token(token_type='',access_token='')
# b=a.json()
# Token.json_encoder(b)
# Token.schema(b)


class TokenScopesTypes(str, enum.Enum):
	ADMIN = "admin"
	ME = "me"
	POSTS = "posts"


class JwtClaims(py_main.BaseModel):
	"""model class for creating jwt claims"""
	
	# typ
	sub: str
	admin: typing.Optional[bool] = None
	iss: typing.Optional[str] = settings.JWT_ISSUER
	exp: typing.Optional[dt.timedelta] = None
	iat: typing.Optional[dt.datetime] = py_fields.Field(
		default_factory=dt.datetime.utcnow
	)
	aud: typing.Optional[py_net.HttpUrl] = py_fields.Field(
		default_factory=lambda: settings.FRONTEND_ORIGIN
	)
	nbf: typing.Optional[int] = None


def get_at_exp():
	return dt.datetime.utcnow() + dt.timedelta(
		minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES
	)


def get_rt_exp() -> dt.datetime:
	return dt.datetime.utcnow() + dt.timedelta(
		days=settings.REFRESH_TOKEN_EXPIRATION_DAYS
	)


class AccessTokenJwtClaims(JwtClaims):
	scopes: typing.List[scope_service.ScopeTypes] = []
	exp: dt.datetime = py_fields.Field(default_factory=get_at_exp)
	
	@property
	def exp_timestamp(self):
		return self.exp.timestamp()


class RefreshTokenJwtClaims(JwtClaims):
	jti: uuid.UUID = py_fields.Field(default_factory=uuid.uuid4)
	exp: dt.datetime = py_fields.Field(default_factory=get_rt_exp)
	
	@property
	def exp_timestamp(self):
		return self.exp.timestamp()


class AccessRefreshedForResponse(AccessTokenJwtClaims):
	token_type: str = py_fields.Field(default='bearer')
	access_token: str
	expiration_time: typing.Optional[dt.datetime]
	expiration_timestamp: typing.Optional[dt.datetime]
	audience: typing.Optional[py_net.HttpUrl]
	
	@py_validators.root_validator(pre=True)
	def set_timestamp(cls, values):
		values["expiration_time"] = values["exp"]
		values["audience"] = values["aud"]
		values["expiration_timestamp"] = values["exp"].strftime('%s')
		return values
