# import dataclasses
# import typing
# import datetime
#
# import fastapi as fast
# import pydantic
# import sqlalchemy.orm.session as sql_session
# import apps.users.models as u_models
# import apps.scopes.schemas as s_schemas
# import apps.token.schemas as t_schemas
# import services.scopes as scope_service
# import services.security_service as security_service
# import apps.token.protocols as t_proto
# from core.base_settings import settings
# from core.database.session import get_session
# from . import components
# import jose.jwt as jwt
#
# # AccessTokenClaimsFactory = t_schemas.AccessClaimsFactory()
# # RefreshTokenClaimsFactory = t_schemas.RefreshClaimsFactory()
#
#
# async def add_user_scopes(user: u_models.User) -> typing.List[scope_service.ScopeTypes]:
# 	"""get user and add all user scopes in db to a list and return it"""
# 	if user.is_admin:
# 		return ["admin"]
# 	else:
# 		scope: s_schemas.ScopeOut
# 		# for scope in form_data.scopes:
# 		# 	if scope.lower() == 'me':
# 		# 		allowed_scopes.append('me')
# 		# 	if scope.lower() == 'posts':
# 		# 		allowed_scopes.append('posts')
# 		allowed_scopes = [scope.code for scope in user.scopes]
# 		return allowed_scopes
#
#
# async def create_refresh_token(user: u_models.User, claims: t_schemas.JwtClaims) -> t_schemas.JwtClaims:
# 	try:
# 		claims.scopes = await add_user_scopes(user=user)
# 		claims.sub = user.username
# 		claims.token = await security_service.create_token(jwt_claims=claims)
#
# 	except (pydantic.ValidationError, jwt.JWSError):
# 		raise fast.HTTPException(
# 			status_code=fast.status.HTTP_403_FORBIDDEN,
# 			detail="Not a valid refresh token, please login again",
# 		)
# 	return claims
#
#
# # async def create_access_token(
# # 	sub: str,
# # 	scopes: list,
# # 	claims: t_schemas.JwtClaims
# # ) -> t_schemas.JwtClaims:
# # 	try:
# # 		claims.sub = sub
# # 		claims.scopes = scopes
# # 		claims.token = await security_service.create_token(jwt_claims=claims)
# # 	except (pydantic.ValidationError, jose.JWSError):
# # 		raise fast.HTTPException(
# # 			status_code=fast.status.HTTP_403_FORBIDDEN,
# # 			detail="Not a valid refresh token, please login again",
# # 		)
# # 	return claims
#
#
# def create_access_token(data: dict, expires_delta: typing.Optional[datetime.timedelta] = None):
# 	to_encode = data.copy()
# 	if expires_delta:
# 		expire = datetime.datetime.utcnow() + expires_delta
# 	else:
# 		expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
# 	to_encode.update({"exp": expire})
# 	encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY, algorithm=settings.ALGORITHM)
# 	return encoded_jwt
#
#
# async def access_token_from_refresh_token(
# 	refresh_token: components.oauth2_refresh_token_reader = fast.Depends(),
# 	claims: t_schemas.JwtClaims = fast.Depends(t_schemas.JwtClaims.access_token)
# ) -> t_schemas.JwtClaims:
# 	try:
# 		payload = await security_service.decode_token(refresh_token)
# 		claims.sub = payload.get("sub", None)
# 		claims.scopes = payload.get("scopes", None)
# 		claims.token = await security_service.create_token(jwt_claims=claims)
# 	except (pydantic.ValidationError, jwt.JWSError, jwt.ExpiredSignatureError):
# 		raise fast.HTTPException(
# 			status_code=fast.status.HTTP_403_FORBIDDEN,
# 			detail="Not a valid refresh token, please login again",
# 		)
#
# 	return claims
#
# # jwt_service = components.JWTService(jwt_verifier=verifier, jwt_creator=creator)
# # Authorizer: t_proto.JWTAuthorizerProtocol = components.JWTAuthorizer(
# # 	jwt_service=jwt_service, cookie_writer=oauth2_refresh_token_writer
# # )
# # @attr.s(hash=True, slots=True, cache_hash=True, frozen=True, kw_only=True)
