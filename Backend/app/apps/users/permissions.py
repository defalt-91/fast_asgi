from fastapi import HTTPException, status, Query
from . import crud_user


class UserIsCurrentOrSudo:
	def __init__(self, current_user, user):
		self.current_user = current_user
		self.user = user
	
	def has_permission(self):
		if not crud_user.user.is_superuser(self.current_user) and (self.current_user.id != self.user.id):
			raise HTTPException(detail="Not enough permissions", status_code=status.HTTP_401_UNAUTHORIZED)


class IsAuthorOrSudo:
	def __init__(self, obj, current_user):
		self.obj = obj
		self.current_user = current_user
	
	def has_permission(self):
		if not crud_user.user.is_superuser(self.current_user) and (self.obj.author_id != self.current_user.id):
			raise HTTPException(detail="Not enough permissions", status_code=status.HTTP_401_UNAUTHORIZED)
