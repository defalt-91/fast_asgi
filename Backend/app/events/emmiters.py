import apps.users.schemas as u_schema
from .events import Events, post_event
from pydantic import EmailStr


def emmit_user_creation_action(registered_user: u_schema.UserCreate):
	post_event(Events.USER_REGISTER, registered_user)


def emmit_password_reset_start_action(email: EmailStr):
	post_event(Events.PASSWORD_RESET, data=email)
