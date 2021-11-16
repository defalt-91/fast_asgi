import uuid
from datetime import datetime

import apps.users.schemas as u_schema
from apps.token.schemas import JwtClaims
from .events import Events, post_event
from pydantic import EmailStr


def emmit_user_creation_action(registered_user: u_schema.UserCreate):
	post_event(Events.USER_REGISTER, registered_user)


def emmit_password_reset_start_action(email: EmailStr):
	post_event(Events.PASSWORD_RESET, data=email)


def emmit_refresh_token_creation(session, user_id, refresh_token_claims: JwtClaims, token: str):
	data = dict(
		session=session, user_id=user_id, expire_at=refresh_token_claims.exp, jti=refresh_token_claims.jti, jwt=token
	)
	post_event(Events.REFRESH_TOKEN_GENERATE, data=data)
