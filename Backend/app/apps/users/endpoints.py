from fastapi import Depends
from fastapi import Security
from fastapi.routing import APIRouter
from .schemas import User
from services.security import get_current_active_user, get_current_user, oauth2_scheme
# from ...configurations.settings_json import cors_configs,
from configurations.settings_env import settings

user_router = APIRouter()


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
