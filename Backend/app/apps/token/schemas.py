import uuid
import datetime as dt
import enum
import typing
import pydantic.main as py_main
import services.scopes as scope_service
import core.base_settings as b_settings
import pydantic.fields as py_fields
import pydantic.networks as py_net
import pydantic.types as py_types


settings = b_settings.get_settings()


def datetime_aware():
	return dt.datetime.now(tz=dt.timezone.utc)


class TokenTypes(str, enum.Enum):
	ACCESS_TOKEN = "access_token"
	REFRESH_TOKEN = "refresh_token"


class TokenPayload(py_main.BaseModel):
	sub: typing.Optional[int] = None


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
	jti: py_types.UUID4


class TokenUpdate(TokenInDBBase):
	pass


class JwtClaims(py_main.BaseModel):
	"""model class for creating jwt claims"""
	
	sub: typing.Optional[str] = None
	scopes: typing.Optional[list[scope_service.ScopeTypes]] = None
	iss: str = settings.JWT_ISSUER
	exp: typing.Optional[dt.datetime] = None
	iat: dt.datetime = py_fields.Field(default_factory=datetime_aware)
	aud: py_net.HttpUrl = py_fields.Field(default_factory=lambda: settings.FRONTEND_ORIGIN)
	nbf: typing.Optional[int] = None
	token: typing.Optional[str] = None
	jti: typing.Optional[py_types.UUID4] = None
	token_type: typing.Optional[TokenTypes] = None
	
	@staticmethod
	def get_access_token_exp():
		return dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
	
	@staticmethod
	def get_refresh_token_exp() -> dt.datetime:
		return dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
	
	@staticmethod
	def create_uuid4() -> py_types.UUID4:
		return uuid.uuid4()
	
	@property
	def exp_timestamp(self):
		return self.exp.timestamp()
	
	@classmethod
	def access_token(cls, sub, scopes):
		""" first way to create claims for token creation (using awesome classmethod as alternative constructor) """
		return cls(exp=cls.get_access_token_exp(), token_type=TokenTypes.ACCESS_TOKEN, sub=sub, scopes=scopes)
	
	@classmethod
	def refresh_token(cls):
		""" first way to create claims for token creation (using awesome classmethod as alternative constructor) """
		return cls(exp=cls.get_refresh_token_exp(), token_type=TokenTypes.REFRESH_TOKEN, jti=cls.create_uuid4())


def claims_access_factory() -> JwtClaims:
	""" second but better way for token claims creation with factory function"""
	return JwtClaims.access_token()


def claims_refresh_factory() -> JwtClaims:
	""" second but better way for token claims creation with factory function"""
	return JwtClaims.refresh_token()


class AccessClaimsFactory:
	""" third way (FastAPI) way for claims creation """
	
	def __init__(self):
		""" all these variables are cached """
		self.issuer = settings.JWT_ISSUER
		self.audience = settings.FRONTEND_ORIGIN
		self.token_type = TokenTypes.ACCESS_TOKEN
		self.expiration_minutes = dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
	
	def __call__(self) -> JwtClaims:
		""" just this part is going to execute with FastAPI dependency injection system"""
		exp = dt.datetime.now(tz=dt.timezone.utc) + self.expiration_minutes
		return JwtClaims(token_type=self.token_type, aud=self.audience, iss=self.issuer, exp=exp)


class RefreshClaimsFactory:
	""" third way (FastAPI) way for claims creation """
	
	def __init__(self):
		""" all these variables are cached """
		self.issuer = settings.JWT_ISSUER
		self.audience = settings.FRONTEND_ORIGIN
		self.token_type = TokenTypes.REFRESH_TOKEN
		self.refresh_token_expiration_days = settings.REFRESH_TOKEN_EXPIRATION_DAYS
	
	def __call__(self) -> JwtClaims:
		""" just this part is going to execute with FastAPI dependency injection system"""
		exp = dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=self.refresh_token_expiration_days)
		jti = uuid.uuid4()
		return JwtClaims(token_type=self.token_type, aud=self.audience, iss=self.issuer, exp=exp, jti=jti)


class RefreshTokenResponse(py_main.BaseModel):
	refresh_token: typing.Optional[str] = None
	expiration_datetime: typing.Optional[dt.datetime] = None


class TokenResponse(py_main.BaseModel):
	token_type: str = py_fields.Field(default="bearer")
	access_token: str
	expiration_datetime: dt.datetime
	refresh_token: typing.Optional[RefreshTokenResponse]
