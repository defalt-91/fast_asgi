from dataclasses import dataclass, field
from starlette.responses import Response
from starlette.requests import Request
from starlette import status
from core.base_settings import get_settings
from typing import Literal, Optional
from fastapi import HTTPException,security
from pydantic import ValidationError
from jose import jwt
import uuid
from .protocols import JWTServiceProtocol, JwtClaims, JWTVerifierProtocol, JWTCreatorProtocol, CookieWriterProtocol


# cached settings
settings = get_settings()

Jwt_Options = {
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


@dataclass(frozen=True)
class GetRefreshToken:
	cookie_name: str
	
	def __call__(self, request: Request) -> str:
		refresh_token: str = request.cookies.get(self.cookie_name)
		if not refresh_token:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="You are not authorize to get a new token, please to go to login page",
			)
		return refresh_token


@dataclass(frozen=True)
class WriteRefreshTokenCookie:
	cookie_name: str
	
	def __call__(self, cookie_value: str, response: Response):
		response.set_cookie(
			key=self.cookie_name, value=cookie_value, httponly=True, path="/", secure=False,
			samesite="strict",  # sending just to the site that wrote the cookie
			expires=settings.REFRESH_TOKEN_EXPIRATION_DAYS * 24 * 60 * 60,
			# domain="myawesomesite.io",  # subdomains are ignored , like api.myawesomesite.io ... just the domain is
			# needed
		)


@dataclass(frozen=True)
class JWTCreator:
	headers: dict = field(default_factory=lambda: {"alg": settings.ALGORITHM, "typ": "JWT"})
	secret_key: str = field(default_factory=lambda: settings.SECRET_KEY)
	algorithm: str = field(default_factory=lambda: settings.ALGORITHM)
	
	def __call__(
		self, claims: JwtClaims, token_type: Literal["access_token", "refresh_token"] = 'access_token'
	):
		try:
			if token_type == 'refresh_token':
				claims.jti = str(claims.jti)
			token = jwt.encode(
				claims=claims.dict(exclude_none=True), key=self.secret_key, algorithm=self.algorithm,
				headers=self.headers
			)
			# claims.jti = uuid.UUID(claims.jti)
			return token
		except(ValidationError, jwt.JWTError):
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="jwt didnt created")


@dataclass(frozen=True)
class JWTVerifier:
	secret_key: str = field(default_factory=lambda: settings.SECRET_KEY)
	algorithm: str = field(default_factory=lambda: settings.ALGORITHM)
	issuer: str = field(default_factory=lambda: settings.JWT_ISSUER)
	audience: str = field(default_factory=lambda: settings.FRONTEND_ORIGIN)
	options: dict = field(default_factory=lambda: Jwt_Options)
	
	def __call__(self, token: str) -> Optional[dict]:
		try:
			token = jwt.decode(
				token=token,
				key=self.secret_key,
				algorithms=[self.algorithm],
				issuer=self.issuer,
				audience=self.audience,
				options=self.options
			)
		
		except jwt.ExpiredSignatureError:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="signature has expired, you need to log in again"
			)
		except jwt.JWTClaimsError:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Your token claims is unacceptable"
			)
		except jwt.JWTError:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="your credentials are not valid, signature is invalid"
			)
		return token


# @dataclass
# class JWTService:
# 	jwt_verifier: JWTVerifierProtocol
# 	jwt_creator: JWTCreatorProtocol
#
#
# @dataclass
# class JWTAuthorizer:
# 	jwt_service: JWTServiceProtocol
# 	cookie_writer: CookieWriterProtocol
