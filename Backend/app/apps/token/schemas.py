import uuid
import datetime as dt
import enum
import typing
import pydantic
import pydantic.main as py_main
import pydantic.fields as py_fields
import pydantic.networks as py_net
import pydantic.types as py_types
import core.base_settings as b_settings


settings = b_settings.get_settings()


class TokenTypes(str, enum.Enum):
	ACCESS_TOKEN = "bearer"
	REFRESH_TOKEN = "refresh_token"


class TokenInDBBase(py_main.BaseModel):
	jwt: str
	user_id: int
	expire_at: dt.datetime
	revoked: bool
	jti: uuid.UUID


class RefreshTokenInDB(TokenInDBBase):
	created_at: dt.datetime
	expire_at: dt.datetime
	revoked: bool = py_fields.Field(default=0)
	
	class Config:
		orm_mode = True


class RefreshTokenCreate(TokenInDBBase):
	revoked: bool = 0
	
	@pydantic.validator("jti", pre=True)
	def str_to_uuid4(cls, v):
		return uuid.UUID(v)


class TokenUpdate(TokenInDBBase):
	revoked: bool = py_fields.Field(default=1)


class JwtClaims(py_main.BaseModel):
	""" class variables for caching them """
	# audience: typing.ClassVar[str] = py_fields.Field(init=False, default=settings.FRONTEND_ORIGIN)
	# issuer: typing.ClassVar[str] = py_fields.Field(init=False, default=settings.JWT_ISSUER)
	# access_token_exp_minutes: typing.ClassVar[int] = attr.field(
	# 	init=False,
	# 	default=settings.ACCESS_TOKEN_EXPIRATION_MINUTES
	# )
	# refresh_token_exp_days: typing.ClassVar[int] = attr.field(
	# 	init=False,
	# 	default=settings.REFRESH_TOKEN_EXPIRATION_DAYS
	# )
	""" model class for creating jwt claims """
	sub: str
	exp: dt.datetime
	iat: dt.datetime
	iss: str
	aud: py_net.HttpUrl
	scopes: str
	token: typing.Optional[str] = None
	jti: typing.Optional[py_types.UUID4] = None
	nbf: typing.Optional[int] = None
	
	@classmethod
	def get_access_token_exp(cls) -> dt.datetime:
		return dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
	
	@classmethod
	def get_refresh_token_exp(cls) -> dt.datetime:
		return dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
	
	@staticmethod
	def create_uuid4() -> py_types.UUID4:
		return uuid.uuid4()
	
	@property
	def exp_timestamp(self):
		return self.exp.timestamp()
	
	@classmethod
	def access_token(cls, subject_id: str, scopes: str):
		""" factory way for token creation (using awesome classmethod as alternative constructor) """
		return cls(
			sub=subject_id,
			aud=settings.FRONTEND_ORIGIN,
			scopes=scopes,
			exp=cls.get_refresh_token_exp(),
			iat=dt.datetime.now(tz=dt.timezone.utc),
			iss=settings.JWT_ISSUER,
		)
	
	@classmethod
	def refresh_token(cls, subject_id: str, scopes: str):
		""" factory way for token creation (using awesome class method as alternative constructor) """
		return cls(
			sub=subject_id,
			aud=settings.FRONTEND_ORIGIN,
			scopes=scopes,
			exp=cls.get_refresh_token_exp(),
			iat=dt.datetime.now(tz=dt.timezone.utc),
			iss=settings.JWT_ISSUER,
			jti=cls.create_uuid4()
		)


# class RefreshTokenResponse(py_main.BaseModel):
# 	refresh_token: typing.Optional[str] = None
# 	expiration_datetime: typing.Optional[dt.datetime] = None


class TokenResponse(py_main.BaseModel):
	token_type: str = py_fields.Field(default="bearer")
	access_token: str
	expiration_datetime: dt.datetime
	# refresh_token: typing.Optional[RefreshTokenResponse]


# class Token(py_main.BaseModel):
# 	access_token: str
# 	token_type: str


# class SecurityScopesList(py_main.BaseModel):
# 	scopes: typing.Optional[list[str]] = py_fields.Field(default_factory=list)
#
# 	@pydantic.validator("scopes", pre=True)
# 	def change_str_to_list(cls, v: str):
# 		return v.split(" ")


# class SecurityScope:
# 	def __init__(self, scope_str: str):
# 		self.scope_str = scope_str
# 		self.scopes = scope_str.split(' ')

# def claims_access_factory() -> JwtClaims:
# 	""" second but better way for token claims creation with factory function"""
# 	return JwtClaims.access_token()
#
#
# def claims_refresh_factory() -> JwtClaims:
# 	""" second but better way for token claims creation with factory function"""
# 	return JwtClaims.refresh_token()
#
#
# class AccessClaimsFactory:
# 	""" third way (FastAPI) way for claims creation """
#
# 	def __init__(self):
# 		""" all these variables are cached """
# 		self.issuer = settings.JWT_ISSUER
# 		self.audience = settings.FRONTEND_ORIGIN
# 		self.token_type = TokenTypes.ACCESS_TOKEN
# 		self.expiration_minutes = dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRATION_MINUTES)
#
# 	def __call__(self) -> JwtClaims:
# 		""" just this part is going to execute with FastAPI dependency injection system"""
# 		exp = dt.datetime.now(tz=dt.timezone.utc) + self.expiration_minutes
# 		return JwtClaims(token_type=self.token_type, aud=self.audience, iss=self.issuer, exp=exp)
#
#
# class RefreshClaimsFactory:
# 	""" third way (FastAPI) way for claims creation """
#
# 	def __init__(self):
# 		""" all these variables are cached """
# 		self.issuer = settings.JWT_ISSUER
# 		self.audience = settings.FRONTEND_ORIGIN
# 		self.token_type = TokenTypes.REFRESH_TOKEN
# 		self.refresh_token_expiration_days = settings.REFRESH_TOKEN_EXPIRATION_DAYS
#
# 	def __call__(self) -> JwtClaims:
# 		""" just this part is going to execute with FastAPI dependency injection system"""
# 		exp = dt.datetime.now(tz=dt.timezone.utc) + dt.timedelta(days=self.refresh_token_expiration_days)
# 		jti = uuid.uuid4()
# 		return JwtClaims(token_type=self.token_type, aud=self.audience, iss=self.issuer, exp=exp, jti=jti)
