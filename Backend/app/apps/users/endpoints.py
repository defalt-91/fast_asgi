from typing import Any, List
from fastapi import Depends
from fastapi.routing import APIRouter
from . import schemas
from . import user_service, models

accounts = APIRouter()


@accounts.get("/", response_model=List[schemas.User])
async def read_users(users=Depends(user_service.user_list)):
	return users


@accounts.post('/', response_model=schemas.User)
async def create_superuser_with_superuser(*, user_created_back_data=Depends(user_service.create_superuser)):
	return user_created_back_data


@accounts.put("/me", response_model=schemas.User, response_model_exclude={'is_superuser', 'is_active'})
def update_user_me(*, user: models.User = Depends(user_service.update_user_me)) -> Any:
	return user


@accounts.get("/me", response_model=schemas.User)
async def read_user_me(user=Depends(user_service.read_user_me)):
	return user


@accounts.post("/open", response_model=schemas.User, response_model_exclude={'is_superuser', 'is_active', 'id'})
async def create_user_open(*, user_created_back_data: models.User = Depends(user_service.create_user)):
	return user_created_back_data


@accounts.get('/{user_id}')
async def read_user_by_id(user: models.User = Depends(user_service.read_user_by_id)):
	return user


@accounts.put("/{user_id}", response_model=schemas.User)
def update_user_by_id(user=Depends(user_service.update_user_by_id)):
	return user


@accounts.delete("/{user_id}", response_model=schemas.User)
def delete_user_by_id(user=Depends(user_service.deactivate_user_by_id)):
	return user
