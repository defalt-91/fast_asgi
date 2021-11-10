import events.events as ev
import apps.users.models as u_models
import logging
import apps.users.schemas as u_schemas
import apps.token.schemas as t_schema
import fastapi.param_functions as fast_params
import core.database.session as core_session
import sqlalchemy.orm.session as sql_session

import apps.token.TokenDAL as t_d


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def registered_user(user: u_schemas.UserCreate):
	msg = (
		f"{logger.name} {logger.level} {u_models.User.username} is registered "
		f"in system :: sending email to {u_models.User.email}"
	)
	logger.info(msg=msg)


# send_new_account_email(
#     email_to=user.email, username=user.username, password=user.hashed_password
# )
def refresh_save_to_db(data):
	print(data)
	t_d.token_dal.create_refresh_token(
		session=data["session"], user_id=data["user_id"], refresh_claims=data["claims"],
	)


def subscribe_to_refresh_creation():
	ev.subscribe(event_type=ev.Events.REFRESH_TOKEN_GENERATE, func=refresh_save_to_db)


def subscribe_to_user_registration():
	ev.subscribe(event_type=ev.Events.USER_REGISTER, func=registered_user)


def subscribe_to_user_login():
	ev.subscribe(ev.Events.REFRESH_TOKEN_GENERATE, refresh_save_to_db)
