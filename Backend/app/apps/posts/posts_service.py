from typing import Optional

from apps.posts.crud_posts import crud_post
from sqlalchemy.orm.session import Session
from fastapi import status, HTTPException, Depends, Security, Query

from apps.posts.model import Post
from apps.posts.schema import PostUpdate, PostCreate
from apps.users.models import User
from services.db_service import get_db

from apps.users.user_service import Permissions
from services.security_service import get_current_active_user


class PostServices:
	@staticmethod
	async def post_update(
		*,
		post_id: int,
		update_data: PostUpdate,
		db: Session = Depends(get_db),
		current_user=Security(get_current_active_user, scopes=["posts"])
	):
		db_obj = crud_post.get(db=db, id=post_id)
		if not db_obj:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='there no such a post')
		is_author = Permissions.IsAuthor(db_obj=db_obj, current_user=current_user)
		if not is_author:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you are not this post Author !')
		try:
			post = crud_post.update(db=db, db_obj=db_obj, obj_in=update_data)
		except ValueError:
			raise HTTPException(detail='the data is not valid', status_code=status.HTTP_400_BAD_REQUEST)
		return post
	
	@staticmethod
	async def post_delete(
		*,
		obj_id: int,
		db: Session = Depends(get_db),
		current_user: User = Security(get_current_active_user, scopes=['me', 'posts']),
	):
		# is_author = Permissions.IsAuthor(db_obj=db_obj, current_user=current_user)
		# if not is_author:
		# 	raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you are not this post Author !')
		obj = db.query(Post).get(obj_id)
		if not obj:
			raise HTTPException(detail='There is no post with this id', status_code=status.HTTP_400_BAD_REQUEST)
		username = obj.author.username
		is_author = Permissions.IsAuthor(current_user=current_user, obj_author_username=username)
		if not is_author:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you are not this post Author !')
		deleted = crud_post.remove(db=db, obj=obj)
		return deleted
	
	@staticmethod
	async def post_create(
		*,
		obj_in: PostCreate,
		db: Session = Depends(get_db),
		current_user=Security(get_current_active_user, scopes=["posts"])
	):
		post_created = crud_post.create_with_author(
			db=db, author_id=current_user.id,
			obj_in=obj_in
		)
		return post_created
	
	@staticmethod
	async def post_detail(
		*,
		post_id: int,
		db: Session = Depends(get_db),
		current_user=Security(get_current_active_user, scopes=["posts"])
	):
		
		post = crud_post.get(db=db, id=post_id)
		if not post:
			raise HTTPException(detail='There is no post with this id', status_code=status.HTTP_400_BAD_REQUEST)
		return post
	
	@staticmethod
	async def post_list(
		*,
		db: Session = Depends(get_db),
		paginated_page: Optional[int] = 1
	):
		if paginated_page <= 1:
			posts = crud_post.get_multi(db=db, limit=5)
		else:
			skip = paginated_page - 1
			posts = crud_post.get_multi(db=db, skip=skip * 5, limit=5)
		if not posts:
			raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='There is no post')
		return posts
