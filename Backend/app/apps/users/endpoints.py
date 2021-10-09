from fastapi import Depends
from fastapi import Security
from fastapi.routing import APIRouter
from .schemas import  User
from services.security import get_current_active_user, get_current_user
from core.base_settings import settings
from .user_service import create_user

user_router = APIRouter()


@user_router.post(
		"/register",
		response_model=User,
		response_model_exclude={"is_active"},
		response_model_by_alias=True,
		)
async def create_user(
		user_created_back_data=Depends(create_user),
):
	if user_created_back_data:
		return user_created_back_data


@user_router.get("/profile/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
	return current_user


@user_router.get("/profile/items/")
async def read_own_items(
		current_user: User = Depends(
				get_current_active_user,
		)
):
	return [{"item_id": "Foo", "owner": current_user.username}]


@user_router.get("/status/")
async def read_system_status():
	return {"status": "ok", "ao": settings.ALLOWED_HOSTS}


@user_router.get("/")
async def user_home(user: User = Security(get_current_user, scopes=['me', ])):
	return {"dict": user}
