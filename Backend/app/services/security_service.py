import uuid
from datetime import timedelta, datetime
from typing import Any, List, Optional
from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes
)

from jose.exceptions import JWTClaimsError
from pydantic import ValidationError

from core.database.session import get_session
from . import errors
from .scopes import all_scopes
from apps.token.schemas import TokenData
from apps.users.models import User
from fastapi import status, Request
from jose import ExpiredSignatureError, JWTError, jwt
from core.base_settings import settings
from sqlalchemy.orm.session import Session
from fastapi.security.utils import get_authorization_scheme_param
from slowapi.util import get_remote_address
from slowapi import Limiter
from apps.users.UserDAL import user_dal
import uuid

Jwt_Options = {
    "verify_signature": True,
    "verify_aud": True,
    "verify_iat": True,
    "verify_exp": True,
    "verify_nbf": True,
    "verify_iss": True,
    "verify_sub": True,
    "verify_jti": False,
    "verify_at_hash": True,
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

""" load config for passlib hashing from .ini file """

# limiter = Limiter(key_func=get_ipaddr, default_limits=["3/minute"])
limiter = Limiter(
    key_func=get_remote_address,
    # headers_enabled=True,
    default_limits=["20/minute"],
    # storage_uri="redis://0.0.0.0:6379"
)


# pwd_context_making_changes = pwd_context.load_path(path=Path(__name__).resolve().parent / "services/CryptContext.ini")


class OAuth2PasswordBearerCookieMode(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        token: str = request.cookies.get("authorization")
        scheme, param = get_authorization_scheme_param(token)
        if not token or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerCookieMode(
    tokenUrl="Oauth/token",
    scopes=all_scopes,
)


def create_access_token(
    jti: int,
    data: dict,
    using_jti=True,
    expires_delta: Optional[timedelta] = None,
    created_at: Optional[bool] = True,
    issuer: Optional[str] = "my corporation",
    audience=None,
    # not_before: Optional[int] = 1
):
    if audience is None:
        audience = ["http://myawesomesite.io"]
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    if using_jti:
        to_encode.update({"jti": jti})
    if created_at:
        to_encode.update({"iat": datetime.utcnow()})
    # if not_before:
    # 	to_encode.update({"nbf": datetime.utcnow() + timedelta(seconds=not_before)})

    if issuer:
        to_encode.update({"iss": issuer})
    if audience:
        to_encode.update({"aud": audience})
    encoded_jwt = jwt.encode(
        claims=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

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
        headers = jwt.get_unverified_header(token)
        if headers.get("alg") != "HS256":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="this token is tampered",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="http://myawesomesite.io",
            options=Jwt_Options,
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception()
        try:
            token_scopes: Optional[List[Any]] = payload.get("scopes", [])
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Not acceptable scope",
                headers={"WWW-Authenticate": authenticate_value},
            )
        token_data = TokenData(
            scopes=token_scopes, username=username, jti=payload.get("jti")
        )
    except ExpiredSignatureError:
        raise credentials_exception(
            detail="your credentials are expired, you need to log in again"
        )
    except JWTClaimsError:
        raise credentials_exception(detail="you cant f with us")
    except ValidationError:
        raise credentials_exception(detail=str(ValidationError.errors))
    except JWTError:
        raise credentials_exception()
    user = user_dal.get_user_by_username(session=db, username=token_data.username)
    if user is None:
        raise credentials_exception()
    tokens = user.tokens
    jti = token_data.jti
    for token in tokens:
        if token_data.jti == token_data.jti:
            print("jti is  in jwt ")
            print("jti is  in jwt ")
            print("jti is  in jwt ")
            print("jti is  in jwt ")
            print("jti is  in jwt ")
            print("jti is  in jwt ")
    for scope in security_scopes.scopes:
        # if 'admin' in token_data.scopes:
        # 	return user
        # elif scope not in token_data.scopes:
        # 	raise HTTPException(
        # 		status_code=status.HTTP_401_UNAUTHORIZED,
        # 		detail="Not enough scopes",
        # 		headers={"WWW-Authenticate": authenticate_value},
        # 	)
        if "admin" not in token_data.scopes and scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough scopes",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: User = Security(
        get_current_user,
        scopes=[
            "me",
        ],
    )
) -> User:
    if not current_user.is_active:
        raise errors.inactive_user
    return current_user


def get_current_active_superuser(
    current_user: User = Security(get_current_active_user, scopes=["admin"]),
) -> User:
    return current_user
