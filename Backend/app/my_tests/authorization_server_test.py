import dataclasses
from dataclasses import dataclass, Field, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod, abstractproperty
from typing import List, Literal, Optional
from jose import jwt


# from core.base_settings import get_settings
# from fastapi import status, HTTPException


settings = {
	"JWT_ISSUER": "my_corp",
	"FRONTEND_ORIGIN": "api.myawesomesite.io",
	"ACCESS_TOKEN_EXPIRATION_MINUTES": 1,
	"REFRESH_TOKEN_EXPIRATION_DAYS": 1,
	"ALGORITHM": jwt.ALGORITHMS.HS256,
	"SECRET_KEY": "secret",
}
jwt_options = {
	"verify_signature": True,
	"verify_aud": True,
	"verify_iat": True,
	"verify_exp": True,
	"verify_nbf": False,
	"verify_iss": True,
	"verify_sub": True,
	"verify_jti": False,
	"verify_at_hash": False,
	"require_aud": True,
	"require_iat": True,
	"require_exp": True,
	"require_nbf": False,
	"require_iss": True,
	"require_sub": True,
	"require_jti": False,
	"require_at_hash": False,
	"leeway": 0,
}


@dataclass
class JWTClaims:
	exp: datetime
	sub: str = field(default_factory=str)
	token_type: Literal["access_token", "refresh_token"] = field(default_factory=list)
	iss: str = field(default_factory=lambda: settings["JWT_ISSUER"])
	aud: str = field(default_factory=lambda: settings["FRONTEND_ORIGIN"])
	iat: datetime = field(default_factory=datetime.utcnow)
	scopes: Optional[List[Literal["me", "posts", "items", "admin"]]] = field(default=None)
	
	@property
	def exp_timestamp(self):
		return self.exp.timestamp()
	
	@classmethod
	def access_token(cls, sub: str, scopes: List[Literal["me", "posts", "items", "admin"]]):
		return cls(
			sub=sub,
			token_type="refresh_token",
			scopes=scopes,
			exp=datetime.utcnow() + timedelta(minutes=settings["REFRESH_TOKEN_EXPIRATION_DAYS"])
		)
	
	@classmethod
	def refresh_token(cls):
		return cls(
			token_type="refresh_token", exp=datetime.utcnow() + timedelta(settings["REFRESH_TOKEN_EXPIRATION_DAYS"])
		)


class TokenService(ABC):
	
	# @abstractmethod
	# def authenticate(self, token):
	# 	""" check for sanity of provided jwt token """
	
	@abstractmethod
	def create_token(self, claims_class: JWTClaims):
		""" create jwt tokens with provided claims """
	
	@abstractmethod
	def verify_token(self, token: str) -> JWTClaims:
		""" verify token """


@dataclass
class JwtService(TokenService):
	headers: Optional = field(default_factory=lambda: {"alg": settings["ALGORITHM"], "typ": "JWT"})
	options: Optional = field(default_factory=lambda: jwt_options)
	
	def create_token(self, claims_class) -> str:
		return jwt.encode(
			claims=claims_class.__dict__,
			headers=self.headers,
			key=settings["SECRET_KEY"],
			algorithm=settings["ALGORITHM"],
		)
	
	def verify_token(self, token: str):
		return jwt.decode(
			key=settings["SECRET_KEY"],
			subject="user.username",
			algorithms=[settings["ALGORITHM"]],
			token=token,
			audience="FRONTEND_ORIGIN",
			options=self.options
		)


class Authorization:
	
	def __init__(self, token_service: TokenService):
		self.token_service = token_service
	
	def authenticate(self, token):
		try:
			payload = self.token_service.verify_token(token)
			if not payload:
				return False
			else:
				return True
		except(jwt.ExpiredSignatureError, jwt.JWTError, jwt.JWTClaimsError):
			return False
	
	def create_access_token(
		self, subject: str, scopes: Optional[List[Literal["me", "posts", "items", "admin"]]] = None
	):
		claims = JWTClaims.access_token(sub=subject, scopes=scopes)
		return self.token_service.create_token(claims_class=claims)
	
	def create_refresh_token(
		self, subject: str,
	):
		claims = JWTClaims.refresh_token()
		return self.token_service.create_token(claims_class=claims)
	
	def create_access_token_from_refresh_token(self, token: str, subject: str):
		payload = self.token_service.verify_token(token=token)
		assert payload["token_type"] == "refresh_token", "this token is not a refresh token"
		refresh_token_claims = JWTClaims.access_token(sub=subject, scopes=payload["scopes"])
		return self.token_service.create_token(claims_class=refresh_token_claims)


if __name__ == "__main__":
	# try:
	jwt_service = JwtService()
	jwt_authorization = Authorization(token_service=jwt_service)
	token = jwt_authorization.create_access_token(subject='user.username', scopes='user.scopes')
	# 	print("access_token", token)
	# 	refreshed = a.create_access_token_from_refresh_token(token=token, subject="user.username")
	# 	print('from refreshed', refreshed)
	# 	print(a.token_service.verify_token(token))
	print(jwt_authorization.authenticate(token))
	print(jwt_authorization.authenticate(token))
# except (jwt.JWTError, jwt.JWTClaimsError, jwt.ExpiredSignatureError) as e:
# 	print(e)
