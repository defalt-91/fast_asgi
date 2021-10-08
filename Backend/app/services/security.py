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

from .scopes import ScopeTypes, all_scopes
from apps.token.schemas import TokenData
from apps.users.models import User
from apps.users.schemas import UserInDB
from fastapi import status
from jose import ExpiredSignatureError, JWTError, jwt
from core.base_settings import settings

from passlib.context import CryptContext

pwd_context = CryptContext(
		schemes=["bcrypt"],
		deprecated="auto"
)

fake_users_db = {
		"defalt91": {
				"username"       : "defalt91", "full_name": "John Doe", "email": "johndoe@example.com",
				"hashed_password": pwd_context.hash("secret"),
				"is_active"      : True,
		}
}

''' load config for passlib hashing from .ini file '''
# pwd_context_making_changes = pwd_context.load_path(path=Path(__name__).resolve().parent / "services/CryptContext.ini")


oauth2_scheme = OAuth2PasswordBearer(
		tokenUrl="token",
		# refreshUrl='refresh',
		# authorizationUrl='login',
		scopes=all_scopes,
)


def get_password_hash(password):
	return pwd_context.hash(
			password,
			# category="admin"
	)


def verify_password(plain_password, hashed_password):
	return pwd_context.verify(
			secret=plain_password,
			hash=hashed_password,
			category=None
	)


def get_user(db, username: str):
	if username in db:
		user_dict = db[username]
		return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
	user = get_user(db, username)
	if not user:
		return False
	if not verify_password(password, user.hashed_password):
		return False
	return user


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
	to_encode.update({ "exp": expire })
	if using_jit:
		to_encode.update({ 'jit': uuid.uuid4().hex })
	encoded_jwt = jwt.encode(claims=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	return encoded_jwt


async def get_current_user(
		security_scopes: SecurityScopes,
		token: str = Depends(oauth2_scheme)
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
			headers = { "WWW-Authenticate": authenticate_value }
		return HTTPException(
				status_code=status_code,
				detail=detail,
				headers=headers,
		)
	
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		username: str = payload.get("sub")
		if username is None:
			raise credentials_exception()
		try:
			token_scopes: Optional[List[ScopeTypes]] = payload.get("scopes", [])
		except ValidationError as e:
			raise HTTPException(
					status_code=status.HTTP_406_NOT_ACCEPTABLE,
					detail="Not acceptable scope",
					headers={ "WWW-Authenticate": authenticate_value },
			)
		token_data = TokenData(scopes=token_scopes, username=username)
	except ExpiredSignatureError:
		raise credentials_exception(detail="your credentials are expired, you need to log in again")
	except JWTClaimsError:
		raise credentials_exception(detail="you cant f with us")
	except ValidationError:
		raise credentials_exception(detail=str(ValidationError.errors))
	# raise credentials_exception(detail=str(ValidationError.errors))
	except JWTError:
		raise credentials_exception()
	user = get_user(db=fake_users_db, username=token_data.username)
	
	if user is None:
		raise credentials_exception
	for scope in security_scopes.scopes:
		if scope not in token_data.scopes:
			raise HTTPException(
					status_code=status.HTTP_401_UNAUTHORIZED,
					detail="Not enough permissions",
					headers={ "WWW-Authenticate": authenticate_value },
			)
	return user


async def get_current_active_user(
		current_user: User = Security(get_current_user, scopes=["me", ])
):
	if not current_user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Disabled user")
	return current_user
