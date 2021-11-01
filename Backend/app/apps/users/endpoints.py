from fastapi import Depends, Query, APIRouter,File
from typing import Any, Tuple, List
from sqlalchemy.orm.session import Session

from core.base_settings import settings
from core.database.session import get_session
from services import errors
from services.email_service import send_new_account_email
from services.paginator import paginator
from services.security_service import (
    get_current_active_user,
    get_current_active_superuser,
)
from . import models, schemas
from .UserDAL import user_dal
from ..scopes.models import ScopesEnum

accounts = APIRouter()


@accounts.get("/", response_model=List[schemas.User])
async def read_users(
    session: Session = Depends(get_session),
    pagination: Tuple[int, int] = Depends(paginator),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """Retrieve users."""
    skip, limit = pagination
    users = user_dal.get_multi(session=session, limit=limit, skip=skip)
    return users


@accounts.post("/", response_model=schemas.User)
async def create_superuser_with_superuser(
    user_in: schemas.UserCreate,
    current_user=Depends(get_current_active_superuser),
    session: Session = Depends(get_session),
):
    """Create new user with current super_user"""

    if user_in.email:
        conflict_email = user_dal.get_user_by_email(
            session=session, email=user_in.email
        )
        if conflict_email:
            raise errors.email_exist
    conflict_username = user_dal.get_user_by_username(
        session=session, username=user_in.username
    )
    if conflict_username:
        raise errors.username_exist
    user_in.is_superuser = True

    user = user_dal.create(session=session, obj_in=user_in)
    if not user:
        raise errors.something_bad_happened
    user_dal.add_user_scope(session=session, user=user, scope=ScopesEnum.ADMIN)
    return user


@accounts.put(
    "/me",
    response_model=schemas.User,
    response_model_exclude={"is_superuser", "is_active"},
)
async def update_user_me(
    *,
    user_in: schemas.UserUpdate,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """Update own user."""
    if user_in.email is not None:
        if user_dal.get_user_by_email(session=session, email=user_in.email):
            raise errors.email_exist
    if user_in.username is not None:
        if user_dal.get_user_by_username(session=session, username=user_in.username):
            raise errors.email_exist
    else:
        user_in.username = current_user.username
    user = user_dal.update(session=session, session_model=current_user, obj_in=user_in)
    return user


@accounts.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user


@accounts.post(
    "/open",
    response_model=schemas.User,
    response_model_exclude={"is_superuser", "is_active", "id"},
)
async def create_user_open(
    user_in: schemas.UserCreate, session: Session = Depends(get_session)
) -> models.User:
    """Create new user without the need to be logged in."""
    if not settings.USERS_OPEN_REGISTRATION:
        raise errors.open_registration_forbidden
    username_exist = user_dal.check_username_exist(
        session=session, username=user_in.username
    )
    if username_exist:
        raise errors.username_exist
    if user_in.email:
        conflict_email = user_dal.get_user_by_email(
            session=session, email=user_in.email
        )
        if conflict_email:
            raise errors.email_exist
    user_in.is_superuser = False
    user_in_db: models.User = user_dal.create(session=session, obj_in=user_in)
    if not user_in_db:
        raise errors.something_bad_happened
    user_dal.add_user_scope(session=session, user=user_in_db, scope=ScopesEnum.ME)
    user_dal.add_user_scope(session=session, user=user_in_db, scope=ScopesEnum.POSTS)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password1
        )
    return user_in_db


@accounts.get("/{user_id}")
async def read_user_by_id(
    *,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_user),
    user_id: int = Query(...),
) -> Any:
    """Get a specific user by id."""

    user = user_dal.get_object_or_404(session=session, instance_id=user_id)
    if not user:
        raise errors.user_not_exist_id
    if not current_user.is_superuser and current_user.id != user.id:
        raise errors.not_author_not_sudo
    return user


@accounts.put("/{user_id}", response_model=schemas.User)
async def update_user_by_id(
    *,
    session: Session = Depends(get_session),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    """Update a user."""
    db_user = user_dal.get_object_or_404(session=session, instance_id=user_id)
    user = user_dal.update(session=session, session_model=db_user, obj_in=user_in)
    return user


@accounts.patch("/{user_id}", response_model=schemas.User)
def deactivate_user_by_id(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_active_superuser),
) -> Any:
    db_user = user_dal.get_object_or_404(session=session, instance_id=user_id)
    if not db_user:
        raise errors.user_not_exist_username
    return user_dal.deactivate(session=session, user=db_user)



@accounts.post('/profile/pic')
async def profile_picture_test(image:File):
