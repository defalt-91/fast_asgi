from typing import Any, Optional, Tuple

from apps.posts.crud_posts import crud_post
from sqlalchemy.orm.session import Session
from fastapi import status, HTTPException, Depends, Security, Query
from apps.users import crud_user
from apps.posts.model import Post
from apps.posts.schema import PostUpdate, PostCreate
from apps.users.models import User
from services.db_service import get_db
from services.paginator import Pagination
from ..users.permissions import IsAuthorOrSudo
from services.security_service import get_current_active_user
from core.base_settings import settings


class PostServices:
	pagination = Pagination(max_limit=settings.MAXIMUM_ITEMS_PER_PAGE)
	
	@staticmethod
	async def post_list(
		current_user=Security(get_current_active_user, scopes=["posts"]),
		db: Session = Depends(get_db),
		paginator: Tuple[int, int] = Depends(pagination)
	):
		skip, limit = paginator
		if crud_user.user.is_superuser(current_user):
			posts = crud_post.get_multi(db=db, skip=skip, limit=limit)
		else:
			posts = crud_post.get_multi_by_author(db=db, author_id=current_user.id, skip=skip, limit=limit)
		if not posts:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='There is no post')
		return posts
	
	@staticmethod
	async def post_create(
		*,
		post_in: PostCreate,
		db: Session = Depends(get_db),
		current_user=Security(get_current_active_user, scopes=["posts"])
	):
		post_created = crud_post.create_with_author(
			db=db, author_id=current_user.id,
			obj_in=post_in
		)
		return post_created
	
	@staticmethod
	async def post_update(
		post_id: int,
		item_in: PostUpdate,
		db: Session = Depends(get_db),
		current_user=Security(get_current_active_user, scopes=["posts"])
	) -> Any:
		""" Update an item. """
		db_obj = crud_post.get(db=db, id=post_id)
		if not db_obj:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='there no such a post')
		IsAuthorOrSudo(current_user=current_user, obj=db_obj).has_permission()
		post = crud_post.update(db=db, db_obj=db_obj, obj_in=item_in)
		return post
	
	@staticmethod
	async def post_detail(
		*,
		post_id: int,
		db: Session = Depends(get_db),
		current_user=Security(get_current_active_user, scopes=["posts"])
	):
		""" Update an item. """
		db_post = crud_post.get(db=db, id=post_id)
		if not db_post:
			raise HTTPException(detail="Item not found", status_code=status.HTTP_404_NOT_FOUND)
		IsAuthorOrSudo(current_user=current_user, obj=db_post).has_permission()
		return db_post
	
	@staticmethod
	async def post_delete(
		*,
		obj_id: int,
		db: Session = Depends(get_db),
		current_user: User = Security(get_current_active_user, scopes=['posts']),
	):
		""" Delete an item. """
		db_obj = db.query(Post).get(obj_id)
		if not db_obj:
			raise HTTPException(detail='There is no post with this id', status_code=status.HTTP_400_BAD_REQUEST)
		IsAuthorOrSudo(current_user=current_user, obj=db_obj).has_permission()
		deleted = crud_post.remove(db=db, id=obj_id)
		return deleted
