from events import events
from events.events import Events, subscribe
from apps.users.models import User
import logging
from services.email_service import send_new_account_email
from .schemas import UserCreate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def registered_user(user: UserCreate):
    msg = (
        f"{logger.name} {logger.level} {User.username} is registered "
        f"in system :: sending email to {User.email}"
    )
    logger.info(msg=msg)


# send_new_account_email(
#     email_to=user.email, username=user.username, password=user.hashed_password
# )


def subscribe_to_user_registration():
    subscribe(event_type=Events.USER_REGISTER, func=registered_user)
