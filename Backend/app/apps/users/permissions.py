import apps.users.models as u_models
import fastapi.exceptions as fast_exc
import starlette.status as st_status


class UserIsCurrentOrSudo:
	def __init__(self, current_user: u_models.User, user):
		self.current_user = current_user
		self.user = user
	
	def has_permission(self):
		if not self.current_user.is_superuser and (
				self.current_user.id != self.user.id
		):
			raise fast_exc.HTTPException(
				detail="Not enough permissions",
				status_code=st_status.HTTP_401_UNAUTHORIZED,
			)


def is_author_or_sudo(obj, current_user: u_models.User) -> bool:
	if current_user.is_superuser or obj.author_id == current_user.id:
		return True
	return False


def is_author(obj, current_user: u_models.User):
	return current_user.id == obj.author_id


class IsAuthorOrSudo:
	def __init__(self, obj, current_user):
		self.obj = obj
		self.current_user = current_user
	
	def has_permission(self) -> bool:
		if not self.current_user.is_superuser(self.current_user) and (
				self.obj.author_id != self.current_user.id
		):
			raise fast_exc.HTTPException(
				detail="Not enough permissions",
				status_code=st_status.HTTP_401_UNAUTHORIZED,
			)
		return True
