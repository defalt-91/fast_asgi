from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select,desc

from services.base_dal import BaseDAL
from .models import Token
from .schemas import TokenCreate, TokenUpdate
from ..users import models
from apps.token.models import TokenTypes
from ..users.models import User


class TokenDAL(BaseDAL[Token, TokenCreate, TokenUpdate]):
    def create_access_token_with_user(self, session: Session, jwt, user_id):
        pyd_token = TokenCreate(
            user_id=user_id, jwt=jwt, token_type=TokenTypes.ACCESS_TOKEN
        )
        token = self.model(**pyd_token.dict())
        session.add(token)
        session.commit()
        session.refresh(token)
        return token

    def create_refresh_token_with_user(self, session: Session, jwt, user_id):
        pyd_token = TokenCreate(
            user_id=user_id, jwt=jwt, token_type=TokenTypes.REFRESH_TOKEN
        )
        token = self.model(**pyd_token.dict())
        token.token_type = TokenTypes.REFRESH_TOKEN
        session.add(token)
        session.commit()
        session.refresh(token)
        return token

    def get_access_token(self, session: Session, user_id: int) -> Optional[List[Token]]:
        statement = (
            select(self.model)
            .where(self.model.token_type == TokenTypes.ACCESS_TOKEN)
            .where(self.model.user_id == user_id)
        ).order_by(desc(self.model.created_at))

        tokens = session.execute(statement).scalars().all()
        return tokens
        # user=session.get(User,user_id)
        # return user.tokens

token_dal = TokenDAL(Token)
