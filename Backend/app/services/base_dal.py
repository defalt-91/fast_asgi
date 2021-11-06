from sqlalchemy import select, desc,delete,update
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload
from fastapi.encoders import jsonable_encoder

from services import errors


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAL(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
	def __init__(self, model: Type[ModelType]):
		"""
		CRUD object with default methods to Create, Read, Update, Delete (CRUD).

		**Parameters**

		* `model`: A SQLAlchemy model class
		* `schema`: A Pydantic model (schema) class
		"""
		self.model = model
	
	def create(self, session: Session, obj_in: CreateSchemaType):
		created_object = self.model(**obj_in)
		session.add(created_object)
		session.commit()
	
	def get_object_or_404(
		self, session: Session, instance_id: int
	) -> Optional[ModelType]:
		orm_object = session.get(self.model, instance_id)
		if not orm_object:
			raise errors.not_found_error()
		return orm_object
	
	def get_multi(
		self, session: Session, skip: int = 0, limit: int = 10
	) -> Optional[List[ModelType]]:
		
		object_list = (
			session.execute(
				select(self.model)
					.offset(skip)
					.limit(limit)
					.order_by(desc(self.model.id))
					.options(selectinload(self.model.author))
			)
				.scalars()
				.all()
		)
		if not object_list:
			raise errors.not_found_error()
		return object_list
	
	def update(
		self,
		session: Session,
		obj_in: Union[UpdateSchemaType, Dict[str, Any]],
		session_model: ModelType,
	) -> Optional[ModelType]:
		if isinstance(obj_in, dict):
			update_data = obj_in
		else:
			update_data = obj_in.dict(exclude_unset=True)
		db_obj = jsonable_encoder(session_model)
		for field in db_obj:
			if field in update_data:
				setattr(session_model, field, update_data[field])
		# session.add(session_model)
		session.commit()
		# session.execute(
		#  update(self.model).
		#  where(session_model.title == "sandy").
		#  values(fullname="Sandy Squirrel Extraordinaire")
		# )
		return session_model
	
	@staticmethod
	def delete(session: Session, instance) -> Any:
		session.delete(instance)
		session.commit()
	# stmt = delete(User).where(User.name == "squidward").execution_options(synchronize_session="fetch")
	# session.execute(stmt)
	@staticmethod
	def save(session: Session, obj: ModelType) -> ModelType:
		session.add(obj)
		session.commit()
		session.refresh(obj)
		return obj
