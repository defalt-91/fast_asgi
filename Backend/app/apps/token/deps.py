import typing
import fastapi as fast
import jose.exceptions as jose_exc
import pydantic

import apps.users.models as u_models
import apps.scopes.models as s_models
import apps.scopes.schemas as s_schemas
import apps.token.schemas as t_schemas
import services.scopes as scope_service
import services.security_service as security_service
import apps.users.UserDAL as U_Dal


async def add_user_scopes(user: u_models.User) -> typing.List[scope_service.ScopeTypes]:
	""" get user and add all user scopes in db to a list and return it """
	allowed_scopes: typing.List[scope_service.ScopeTypes] = []
	user_scopes: typing.List[s_models.Scope] = user.scopes
	if user.is_admin:
		allowed_scopes.append('admin')
		return allowed_scopes
	else:
		scope: s_models.Scope
		for scope in user_scopes:
			j = s_schemas.ScopeOut.from_orm(scope)
			allowed_scopes.append(j.code)
		return allowed_scopes


class GetRefreshToken:
	async def __call__(self, request: fast.Request):
		refresh_token: str = request.cookies.get("refresh_token")
		if not refresh_token:
			raise fast.HTTPException(
				status_code=fast.status.HTTP_401_UNAUTHORIZED,
				detail="You are not authorize to get a new token, please to go to login page"
			)
		return refresh_token


oauth2_refresh_token = GetRefreshToken()


async def access_token_from_refresh_token(refresh_token: str, session):
	try:
		payload = await security_service.decode_token(refresh_token)
		username = payload.get('sub', None)
		user = U_Dal.user_dal.get_user_by_username(username=username, session=session)
		if not user:
			return None
		allowed_scopes = await add_user_scopes(user)
		access_token_claims = t_schemas.AccessTokenJwtClaims(sub=user.username, scopes=allowed_scopes)
		access_token = security_service.create_access_token(jwt_claims=access_token_claims)
	
	except pydantic.ValidationError:
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="Validation error"
		)
	except jose_exc.ExpiredSignatureError:
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="signature has expired, you need to log in again"
		)
	except jose_exc.JWTClaimsError:
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="Your token claims is unacceptable"
		)
	except jose_exc.JWTError:
		raise fast.HTTPException(
			status_code=fast.status.HTTP_403_FORBIDDEN,
			detail="your credentials are not valid, signature is invalid"
		)
	return access_token
