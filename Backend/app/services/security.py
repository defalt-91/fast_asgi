import uuid
from datetime import timedelta, datetime
from typing import List, Optional
from fastapi import Depends, HTTPException, Security
from fastapi.security import (
	OAuth2PasswordBearer,
	SecurityScopes,
)
from jose.exceptions import JWTClaimsError
from pydantic import ValidationError

from .db_service import get_db
from .scopes import ScopeTypes, all_scopes
from apps.token.schemas import TokenData
from apps.users.models import User
from fastapi import status
from jose import ExpiredSignatureError, JWTError, jwt
from core.base_settings import settings
from apps.users.crud_user import user as crud_user
from sqlalchemy.orm.session import Session

''' load config for passlib hashing from .ini file '''
# pwd_context_making_changes = pwd_context.load_path(path=Path(__name__).resolve().parent / "services/CryptContext.ini")
oauth2_scheme = OAuth2PasswordBearer(
		tokenUrl="token",
		# refreshUrl='refresh',
		# authorizationUrl='login',
		scopes=all_scopes,
)


def create_access_token(
		data: dict,
		using_jit=True,
		expires_delta: Optional[timedelta] = None,
):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	if using_jit:
		to_encode.update({'jit': uuid.uuid4().hex})
	encoded_jwt = jwt.encode(claims=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	return encoded_jwt


async def get_current_user(
		security_scopes: SecurityScopes,
		token: str = Depends(oauth2_scheme),
		db: Session = Depends(get_db)
):
	if security_scopes.scopes:
		authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
	else:
		authenticate_value = f"Bearer"
	
	def credentials_exception(
			headers=None,
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
	):
		if headers is None:
			headers = {"WWW-Authenticate": authenticate_value}
		return HTTPException(
				status_code=status_code,
				detail=detail,
				headers=headers,
		)
	
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		email: str = payload.get("sub")
		if email is None:
			raise credentials_exception()
		try:
			token_scopes: Optional[List[ScopeTypes]] = payload.get("scopes", [])
		except ValidationError:
			raise HTTPException(
					status_code=status.HTTP_406_NOT_ACCEPTABLE,
					detail="Not acceptable scope",
					headers={"WWW-Authenticate": authenticate_value},
			)
		token_data = TokenData(scopes=token_scopes, email=email)
	except ExpiredSignatureError:
		raise credentials_exception(detail="your credentials are expired, you need to log in again")
	except JWTClaimsError:
		raise credentials_exception(detail="you cant f with us")
	except ValidationError:
		raise credentials_exception(detail=str(ValidationError.errors))
	except JWTError:
		raise credentials_exception()
	user = crud_user.get_user_by_email(db=db, email=token_data.email)
	
	if user is None:
		raise credentials_exception
	for scope in security_scopes.scopes:
		if scope not in token_data.scopes:
			raise HTTPException(
					status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Not enough permissions",
					headers={"WWW-Authenticate": authenticate_value},
			)
	return user


async def get_current_active_user(
		current_user: User = Security(get_current_user, scopes=["me", ])
):
	if not current_user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Disabled user")
	return current_user


def get_current_active_superuser(
		current_user: User = Depends(get_current_user),
) -> User:
	# if not crud.user.is_superuser(current_user):
	# 	raise HTTPException(
	# 			status_code=400, detail="The user doesn't have enough privileges"
	# 	)
	return current_user
