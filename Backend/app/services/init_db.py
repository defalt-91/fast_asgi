from sqlalchemy.orm import Session

from apps.users.UserDAL import user_dal
from core.base_settings import settings
from apps.users import schemas


# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = user_dal.get_user_by_username(db, username=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.UserCreate(
            username=settings.FIRST_SUPERUSER,
            password1=settings.FIRST_SUPERUSER_PASSWORD,
            password2=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user_dal.create(db, obj_in=user_in)  # noqa: F841
