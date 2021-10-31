from typing import List, Tuple
from fastapi.routing import APIRouter
from fastapi import Depends, status, HTTPException, Security, Path

from core.database.session import get_scoped_session as get_session
from services import errors
from services.security_service import get_current_active_user
from . import schema
from . import model
from .PostDAL import post_dal
from ..users.models import User
from ..users import permissions
from sqlalchemy.orm.session import Session
from services.paginator import paginator
from ..users import schemas

post_router = APIRouter()


@post_router.get('/', status_code=status.HTTP_200_OK, response_model=List[schema.PostList])
async def post_list(
	current_user=Security(get_current_active_user, scopes=["posts"]),
	pagination: Tuple[int, int] = Depends(paginator),
	session=Depends(get_session)
):
	skip, limit = pagination
	if 'admin' in str(current_user.scopes) and current_user.is_superuser:
		posts = post_dal.get_multi(session=session, skip=skip, limit=limit + 10, model=User)
	else:
		posts = post_dal.get_multi_with_author(session, user=current_user, skip=skip, limit=limit + 10)
	if not posts:
		raise errors.not_found_error
	return posts


@post_router.post('/', status_code=status.HTTP_201_CREATED, response_model=schema.PostDetail)
async def post_create(
	*,
	session=Depends(get_session),
	post_in: schema.PostCreate,
	current_user=Security(get_current_active_user, scopes=["posts"]),

):
	if 'admin' in str(current_user.scopes) and post_in.author_id:
		author_id: int = post_in.author_id
	elif 'admin' in str(current_user.scopes) and not post_in.author_id:
		raise HTTPException(detail="You need to pass author_id", status_code=status.HTTP_406_NOT_ACCEPTABLE)
	else:
		author_id: int = current_user.id
	session_object = post_dal.create_with_author(
		session=session, post_in=post_in, author_id=author_id
	)
	return session_object


@post_router.get('/{post_id}', status_code=status.HTTP_200_OK, response_model=schema.PostDetail)
async def post_detail(
	*,
	post_id: int,
	session=Depends(get_session),
	current_user: User = Security(get_current_active_user, scopes=['posts'])
):
	return post_dal.get_object_with_relations_or_404(session=session, instance_id=post_id)


@post_router.patch(
	'/{post_id}',
	status_code=status.HTTP_201_CREATED,
	response_model=schema.PostDetail
)
async def post_update(
	*,
	post_id: int = Path(..., ge=1),
	obj_in: schema.PostUpdate,
	session: Session = Depends(get_session),
	current_user: User = Security(get_current_active_user, scopes=['posts'])
):
	db_obj: model.Post = post_dal.get_object_or_404(session=session, instance_id=post_id)
	
	if not permissions.is_author_or_sudo(obj=db_obj, current_user=current_user):
		raise errors.not_author_not_sudo
	if obj_in.author_id != db_obj.author_id and current_user.is_superuser:
		user = session.get(User, obj_in.author_id)
		if not user:
			raise errors.user_not_found
	else:
		obj_in.author_id = current_user.id
	post = post_dal.update_post(session=session, pydantic_in=obj_in, session_model=db_obj)
	return post


@post_router.delete('/{post_id}', status_code=status.HTTP_200_OK, response_model=schemas.Msg)
async def post_delete(
	*,
	post_id: int,
	current_user=Security(get_current_active_user, scopes=['posts']),
	session: Session = Depends(get_session),
):
	instance = post_dal.get_object_or_404(instance_id=post_id, session=session)
	if not permissions.is_author_or_sudo(current_user=current_user, obj=instance):
		raise errors.not_author_not_sudo
	post_dal.delete(session=session, instance=instance)
	return {"msg": f"Post with id {post_id} deleted"}
