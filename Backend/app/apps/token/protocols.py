from typing import Optional, Protocol, Literal
from jose.jwt import ALGORITHMS
from fastapi import Response

from apps.token.schemas import JwtClaims


class CookieWriterProtocol(Protocol):
	cookie_name: str
	""" cookie name must be past as class initializer parameter """
	
	def __call__(self, cookie_value: str, response: Response) -> None:
		""" method to write cookie"""


class TokenCreatorProtocol(Protocol):
	def __call__(self, claims: JwtClaims, token_type: Literal["access_token", "refresh_token"]) -> Optional[str]:
		"""Dependency`(Depends)` for creating authentication token"""


class JWTCreatorProtocol(Protocol):
	headers: dict
	secret_key: str
	algorithm: ALGORITHMS
	
	def __call__(self, claims: JwtClaims, token_type: Literal["access_token", "refresh_token"]) -> Optional[str]:
		"""Dependency`(Depends)` for creating jwt authentication token"""


class TokenVerifierProtocol(Protocol):
	def __call__(self, token: str) -> Optional[dict]:
		"""Dependency`(Depends)` for verifying signature of token"""


class JWTVerifierProtocol(Protocol):
	secret_key: str
	algorithm: ALGORITHMS
	issuer: str
	audience: str
	options: dict
	
	def __call__(self, token: str) -> Optional[dict]:
		"""Dependency`(Depends)` for verifying signature of jwt"""


class TokenServiceProtocol(Protocol):
	verifier: TokenVerifierProtocol
	creator: TokenCreatorProtocol


class JWTServiceProtocol(Protocol):
	jwt_verifier: JWTVerifierProtocol
	jwt_creator: JWTCreatorProtocol


class TokenAuthorizerProtocol(Protocol):
	token_service: TokenServiceProtocol
	cookie_writer: Optional[CookieWriterProtocol]


class JWTAuthorizerProtocol(Protocol):
	jwt_service: JWTServiceProtocol
	cookie_writer: CookieWriterProtocol