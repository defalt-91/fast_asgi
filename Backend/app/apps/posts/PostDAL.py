from apps.posts.model import Post
from apps.posts.schema import PostCreate, PostUpdate
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from apps.users.models import User
from services.base_dal import BaseDAL
from services import errors
from sqlalchemy.orm.session import Session
from typing import Any, Dict, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession


class PostDal(BaseDAL[Post, PostUpdate, PostCreate]):
	
	def get_object_with_relations_or_404(self, session: Session, instance_id: int) -> Optional[Post]:
		try:
			query = session.execute(
				select(self.model)
					.where(self.model.id == instance_id)
					.options(
					selectinload(Post.author)
				)
			).scalar_one()
		except:
			raise errors.something_bad_happened
		if not query:
			raise errors.not_found_error
		return query
	
	def get_multi_with_author(self, session: Session, skip: int, limit: int, user: User):
		
		user_posts = session.execute(
			select(self.model)
				.where(self.model.author_id == user.id)
				.offset(skip).limit(limit)
		).scalars().all()
		return user_posts
	
	# def get_multi(self, session: Session, skip: int = 0, limit: int = 10) -> Optional[List[Post]]:
	# 	query = select(self.model).options(
	# 		joinedload(Post.author)
	# 	).offset(skip).limit(limit)
	# 	object_list = session.execute(query).scalars().all()
	# 	if not object_list:
	# 		raise errors.not_found_error
	# 	return object_list
	
	def create_with_author(self, post_in: PostCreate, author_id, session):
		try:
			db_obj = self.model(**post_in.dict())
			session.add(db_obj)
			db_obj.author_id = author_id
			session.commit()
			return db_obj
		except:
			raise errors.something_bad_happened
	
	async def get_posts_async_scoped_session(self, session: AsyncSession):
		stmt = select(Post).limit(10)
		posts = await session.execute(stmt)
		return posts.scalars().all()


post_dal = PostDal(Post)
