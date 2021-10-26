from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Query, scoped_session, sessionmaker
import sqlalchemy as sa
from fastapi import HTTPException, status
from .db_session import SessionLocal as Session

metadata = sa.MetaData()


class BaseQuery(Query):
	def get_or_404(self, ident):
		""" performs a query.get or raises a 404 if not found """
		qs = self.get(ident)
		if not qs:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
		return qs


@as_declarative(metadata=metadata)
class Base:
	id = sa.Column(sa.Integer, primary_key=True)
	
	@declared_attr
	def __tablename__(cls):
		return cls.__name__.lower()
	
	def __repr__(self):
		return f"<{self.__class__.__name__}, id={self.id}>"
	
	def __str__(self):
		return self.__repr__()
	
	# Convenience property to query the database for instances of this model
	# using the current session. Equivalent to ``db.session.query(Model)``
	query: BaseQuery
	
	def save(self) -> None:
		""" save the current instance """
		
		session = Session()
		
		try:
			session.add(self)
			session.commit()
		except:
			session.rollback()
			raise
	
	def delete(self) -> None:
		""" delete the current instance """
		
		session = Session()
		
		try:
			session.delete(self)
			session.commit()
		except:
			session.rollback()
			raise
	
	# def can_be_deleted(self) -> bool:
		"""
		Simple helper to check if the instance has entities
		that will prevent this from being deleted via a protected foreign key.
		"""
	
	# deps = list(
	# 	dependent_objects(
	# 		self,
	# 		(
	# 			fk
	# 			for fk in get_referencing_foreign_keys(self.__class__)
	# 			# On most databases RESTRICT is the default mode hence we
	# 			# check for None values also
	# 			if fk.ondelete == "RESTRICT" or fk.ondelete is None
	# 		),
	# 	).limit(1)
	# )
	
	# return not deps
	
	def refresh_from_db(self) -> None:
		""" Refresh the current instance from the database """
		
		sa.inspect(self).session.refresh(self)
