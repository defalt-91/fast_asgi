import uuid
from datetime import datetime
import datetime as dt

import sqlalchemy.orm.session as sql_ses
import sqlalchemy.sql as sql_sel
import apps.token.schemas as t_schemas
import apps.token.models as t_models
import services.base_dal as base_dal


class TokenDAL(base_dal.BaseDAL[t_models.Token, t_schemas.RefreshTokenCreate, t_schemas.TokenUpdate]):
	
	def get_multi_with_user(self, session: sql_ses.Session, user_id: int):
		"""get user id and return all user tokens"""
		stmt = sql_sel.select(self.model).where(self.model.user_id == user_id). \
			where(self.model.revoked == False). \
			where(self.model.expire_at >= datetime.now(tz=dt.timezone.utc)). \
			order_by(sql_sel.desc(self.model.expire_at))
		tokens = session.execute(stmt).scalars().all()
		return tokens
	
	def create_refresh_token(
		self,
		jwt: str,
		session: sql_ses.Session,
		user_id: int,
		expire_at: datetime,
		jti: uuid.UUID
	):
		pyd_token = t_schemas.RefreshTokenCreate(
			expire_at=expire_at,
			jwt=jwt,
			jti=jti,
			user_id=user_id
		)
		token = self.model(**pyd_token.dict())
		session.add(token)
		session.commit()
		session.refresh(token)
		return token
	
	def get_token(self, session, instance_jti: uuid.UUID):
		stmt = sql_sel.select(self.model).where(self.model.jti == instance_jti)
		token = session.execute(stmt)
		return token.scalar_one_or_none()
	
	def revoke_token(self, session: sql_ses.Session, token: t_models.Token) -> t_models.Token:
		token.revoked = 1
		session.add(token)
		session.commit()
		session.refresh(token)
		return token


# user=session.get(User,user_id)
# return user.tokens


token_dal = TokenDAL(t_models.Token)
