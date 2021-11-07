import typing

import sqlalchemy.orm.session as sql_ses
import sqlalchemy.sql as sql_sel
import sqlalchemy.sql.elements as sql_elem
import apps.token.schemas as t_schemas
import apps.token.models as t_models
from services.base_dal import BaseDAL


class TokenDAL(
	BaseDAL[t_models.Token, t_schemas.RefreshTokenCreate, t_schemas.TokenUpdate]
):
	# def create_access_token_with_user(self, session: Session, jwt, user_id):
	# 	pyd_token = t_schemas.RefreshTokenCreate(
	# 		user_id=user_id, jwt=jwt, token_type=t_schemas.TokenTypes.ACCESS_TOKEN
	# 	)
	# 	token = self.model(**pyd_token.dict())
	# 	session.add(token)
	# 	session.commit()
	# 	session.refresh(token)
	# 	return token
	def get_multi_with_user(self, session: sql_ses.Session, sub: int):
		"""get user id and return all user tokens"""
		stmt = sql_sel.select(self.model).where(self.model.user_id == sub)
		tokens = session.execute(stmt).scalars()
		return tokens
	
	def create_refresh_token(
		self,
		session: sql_ses.Session,
		user_id: int,
		refresh_token: str,
		refresh_claims: t_schemas.RefreshTokenJwtClaims,
	):
		pyd_token = t_schemas.RefreshTokenCreate(
			expire_at=refresh_claims.exp,
			jwt=refresh_token,
			jti=refresh_claims.jti,
			user_id=user_id,
			token_type=t_schemas.TokenTypes.REFRESH_TOKEN,
		)
		token = self.model(**pyd_token.dict())
		session.add(token)
		session.commit()
		session.refresh(token)
		return token
	
	def get_access_tokens(
		self, session: sql_ses.Session, user_id: int
	) -> typing.Optional[typing.List[t_models.Token]]:
		statement = (
			sql_sel.select(self.model)
				.where(self.model.token_type == t_schemas.TokenTypes.REFRESH_TOKEN)
				.where(self.model.user_id == user_id)
		) \
			# .order_by(sql_elem.UnaryExpression.desc(self.model.created_at))
		
		tokens = session.execute(statement).scalars().all()
		return tokens


# user=session.get(User,user_id)
# return user.tokens


token_dal = TokenDAL(t_models.Token)
