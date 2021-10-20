from typing import List, Dict, Any, Optional, Union

from apps.posts.model import Post
from apps.posts.schema import PostCreate,  PostUpdate
from core.base_crud import CRUDBase
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder


class CRUDPost(CRUDBase[Post, PostCreate, PostUpdate]):
	
	def create_with_author(self, db: Session, *, obj_in: PostCreate, author_id: int) -> Post:
		obj_in_data = jsonable_encoder(obj_in)
		db_obj = Post(**obj_in_data, author_id=author_id)
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj
	
	def get_by_author(self, db: Session, author_id: int, skip: int = 0, limit: int = 5) -> List[Post]:
		posts = db.query(Post) \
			.filter(author_id == author_id) \
			.offset(skip) \
			.limit(limit) \
			.all()
		print(type(posts[0].author))
		return posts
	
	def update(
		self,
		db: Session,
		*,
		db_obj: Post,
		obj_in: Union[PostUpdate, Dict[str, Any]]
	) -> Post:
		obj_data = jsonable_encoder(db_obj)
		if isinstance(obj_in, dict):
			update_data = obj_in
		else:
			update_data = obj_in.dict(exclude_unset=True)
		for field in obj_data:
			if field in update_data:
				setattr(db_obj, field, update_data[field])
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj
	
	def remove(self, db: Session, *, obj: Post) -> Optional[Post]:
		db.delete(obj)
		db.commit()
		return obj


crud_post = CRUDPost(Post)
