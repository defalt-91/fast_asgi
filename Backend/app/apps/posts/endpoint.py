from typing import List
from fastapi.routing import APIRouter
from fastapi import Depends, status
from . import schema
from .posts_service import PostServices
from .model import Post

post_router = APIRouter()


@post_router.get('/list', response_model=List[schema.PostList])
async def post_list(posts=Depends(PostServices.post_list)):
	return posts


@post_router.get('/{post_id}', response_model=schema.PostDetail)
async def post_detail(post=Depends(PostServices.post_detail)):
	return post


@post_router.post('/new', response_model=schema.PostDetail)
async def post_create(post_created=Depends(PostServices.post_create)):
	return post_created


@post_router.put('/{post_id}', status_code=status.HTTP_201_CREATED, response_model=schema.PostDetail)
async def post_update(*, post: Post = Depends(PostServices.post_update)):
	return post


@post_router.delete('/{post_id}', response_model=schema.PostDetail, status_code=status.HTTP_200_OK)
async def post_delete(deleted_post=Depends(PostServices.post_delete)):
	return deleted_post
