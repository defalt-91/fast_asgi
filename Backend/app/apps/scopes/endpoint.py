from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from apps.users.models import User
from core.database.session import get_session
from services import errors
from services.security_service import get_current_active_superuser
from . import schemas
from .models import Scope


scope_api = APIRouter()


@scope_api.get("/", response_model=List[schemas.ScopeOut])
async def scope_list(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_superuser),
):
    """scope lists with super_user"""
    return session.execute(select(Scope)).scalars().all()


@scope_api.get("/{scope_id}")
async def scope_detail(
    scope_id: int,
    current_user: User = Depends(get_current_active_superuser),
    session: Session = Depends(get_session),
):
    """scopes details  with super_user"""
    return session.get(Scope, scope_id)


@scope_api.post("/", description="Adding new permission to authentication system")
async def add_new_scope(
    scope: schemas.ScopeIn,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_superuser),
):
    """creating new scopes with super_user"""
    new_scope = Scope()
    new_scope.code = scope.code
    new_scope.description = scope.description
    session.add(new_scope)
    session.commit()
    session.refresh(new_scope)
    return new_scope


@scope_api.get("/users/{scope}", response_model=schemas.ScopeOutWithUsers)
async def scope_users(
    scope: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_superuser),
):
    statement = select(Scope).where(Scope.id == scope)
    scope = session.execute(statement=statement).scalar_one_or_none()
    if not scope:
        raise errors.not_found_error()
    return scope


@scope_api.delete("/{scope_id}")
async def delete_scope(
    scope_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_superuser),
):
    """deleting scopes with super_user, please be caution"""
    wanted_scope = session.get(Scope, scope_id)
    if not wanted_scope:
        raise errors.not_found_error()
    session.delete(wanted_scope)
    session.commit()
    return {
        "msg": f"Scope with code:{wanted_scope.code} and id:{wanted_scope.id} was deleted"
    }
