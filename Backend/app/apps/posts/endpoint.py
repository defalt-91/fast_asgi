import typing
import sqlalchemy.orm.session as sql_sess
import fastapi.exceptions as f_exc
import fastapi.routing as fr
import fastapi.param_functions as fp
import starlette.status as st_s
import core.database.session as sess
import services.errors as my_err
import services.paginator as pg
import apps.posts.PostDAL as PostDAL
import apps.posts.model as model
import apps.posts.schema as schema

import apps.users.permissions as u_perms
import apps.users.schemas as u_schema
import apps.users.models as u_model
import apps.components as components

post_router = fr.APIRouter()


@post_router.get(
    "/", status_code=st_s.HTTP_200_OK, response_model=typing.List[schema.PostList]
)
async def post_list(
    current_user=fp.Security(components.current_active_user, scopes=["posts"]),
    pagination: typing.Tuple[int, int] = fp.Depends(pg.paginator),
    session: sql_sess.Session = fp.Depends(sess.get_session),
):
    skip, limit = pagination
    if "admin" in str(current_user.scopes) and current_user.is_superuser:
        posts = PostDAL.post_dal.get_multi(
            session=session, skip=skip, limit=limit + 10, model=u_model.User
        )
    else:
        posts = PostDAL.post_dal.get_multi_with_author(
            session, user=current_user, skip=skip, limit=limit + 10
        )
    if not posts:
        raise my_err.not_found_error()
    return posts


@post_router.post("/", status_code=st_s.HTTP_201_CREATED, response_model=schema.PostDetail)
async def post_create(
    *,
    post_in:schema.PostCreate,
    session: sql_sess.Session = fp.Depends(sess.get_session),
    current_user=fp.Security(components.current_active_user, scopes=["posts"]),
):
    if "admin" in str(current_user.scopes) and post_in.author_id:
        author_id: int = post_in.author_id
    elif "admin" in str(current_user.scopes) and not post_in.author_id:
        raise f_exc.HTTPException(
            detail="You need to pass author_id",
            status_code=st_s.HTTP_406_NOT_ACCEPTABLE,
        )
    else:
        author_id: int = current_user.id
    session_object = PostDAL.post_dal.create_with_author(
        session=session, post_in=post_in, author_id=author_id
    )
    return session_object


@post_router.get(
    "/{post_id}",
    status_code=st_s.HTTP_200_OK,
    response_model=schema.PostDetail,
    dependencies=[fp.Security(components.current_active_user, scopes=["posts"])],
)
async def post_detail(
    *,
    post_id: int,
    session: sql_sess.Session = fp.Depends(sess.get_session),
    # current_user: u_model.User = Security(
    # 	security_service.get_current_active_user, scopes=["posts"]
    # ),
):
    return PostDAL.post_dal.get_object_with_relations_or_404(
        session=session, instance_id=post_id
    )


@post_router.patch(
    "/{post_id}", status_code=st_s.HTTP_201_CREATED, response_model=schema.PostDetail
)
async def post_update(
    *,
    post_id: int = fp.Path(..., ge=1),
    obj_in: schema.PostUpdate,
    session: sql_sess.Session = fp.Depends(sess.get_session),
    current_user: u_model.User = fp.Security(
        components.current_active_user, scopes=["posts"]
    ),
):
    db_obj: model.Post = PostDAL.post_dal.get_object_or_404(
        session=session, instance_id=post_id
    )
    if not u_perms.is_author_or_sudo(obj=db_obj, current_user=current_user):
        raise my_err.not_author_not_sudo()
    if obj_in.author_id != db_obj.author_id and current_user.is_superuser:
        user = session.get(u_model.User, obj_in.author_id)
        if not user:
            raise my_err.user_not_found()
    else:
        obj_in.author_id = current_user.id
    post = PostDAL.post_dal.update(session=session, obj_in=obj_in, session_model=db_obj)
    return post


@post_router.delete(
    "/{post_id}", status_code=st_s.HTTP_200_OK, response_model=u_schema.Msg
)
async def post_delete(
    *,
    post_id: int,
    current_user=fp.Security(components.current_active_user, scopes=["posts"]),
    session: sql_sess.Session = fp.Depends(sess.get_session),
):
    instance = PostDAL.post_dal.get_object_or_404(instance_id=post_id, session=session)
    if not u_perms.is_author_or_sudo(current_user=current_user, obj=instance):
        raise my_err.not_author_not_sudo()
    PostDAL.post_dal.delete(session=session, instance=instance)
    return {"msg": f"Post with id {post_id} deleted"}
