from apps.posts.model import Post
from apps.posts import schema

import sqlalchemy.orm.strategy_options as sql_strategy
import sqlalchemy.sql as sql_sel

import apps.users.models as u_models
import services.base_dal as base_dal
import services.errors as my_err
import typing
import sqlalchemy.ext.asyncio.session as sql_async
import sqlalchemy.orm.session as sql_ses
import sqlalchemy.exc as sql_exc


class PostDal(
    base_dal.BaseDAL[Post, schema.PostUpdate, schema.PostCreate]
):
    def get_object_with_relations_or_404(
        self, session: sql_ses.Session, instance_id: int
    ) -> typing.Optional[Post]:
        try:
            query = session.execute(
                sql_sel.select(self.model)
                .where(self.model.id == instance_id)
                .options(sql_strategy.selectinload(Post.author))
            ).scalar_one()
        except sql_exc.DataError:
            raise my_err.something_bad_happened()
        if not query:
            raise my_err.not_found_error()
        return query

    def get_multi_with_author(
        self, session: sql_ses.Session, skip: int, limit: int, user: u_models.User
    ):

        user_posts = (
            session.execute(
                sql_sel.select(self.model)
                .where(self.model.author_id == user.id)
                .offset(skip)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return user_posts

    # def get_multi(self, session: Session, skip: int = 0, limit: int = 10) -> Optional[List[Post]]:
    # 	query = select(self.model).options(
    # 		joinedload(Post.author)
    # 	).offset(skip).limit(limit)
    # 	object_list = session.execute(query).scalars().all()
    # 	if not object_list:
    # 		raise my_err.not_found_error
    # 	return object_list

    def create_with_author(self, post_in: schema.PostCreate, author_id, session):
        try:
            db_obj = self.model(**post_in.dict())
            session.add(db_obj)
            db_obj.author_id = author_id
            session.commit()
            return db_obj
        except sql_exc.DataError:
            raise my_err.something_bad_happened()

    async def get_posts_async_scoped_session(
        self, session: sql_async.AsyncSession
    ) -> typing.List[Post]:
        stmt = sql_sel.select(self.model).limit(10)
        posts = await session.execute(stmt)
        return posts.scalars().all()


post_dal = PostDal(Post)
