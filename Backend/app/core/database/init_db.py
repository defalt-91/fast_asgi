from sqlalchemy.orm import Session

from core.base_settings import settings
from apps.users import crud_user, schemas
from core.database import base  # noqa: F401


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
	# Tables should be created with Alembic migrations
	# But if you don't want to use migrations, create
	# the tables un-commenting the next line
	# Base.metadata.create_all(bind=engine)
	
	user = crud_user.user.get_user_by_username(db, username=settings.FIRST_SUPERUSER)
	if not user:
		user_in = schemas.UserCreate(
			username=settings.FIRST_SUPERUSER,
			raw_password=settings.FIRST_SUPERUSER_PASSWORD,
			is_superuser=True,
		)
		crud_user.user.create(db, obj_in=user_in)  # noqa: F841
