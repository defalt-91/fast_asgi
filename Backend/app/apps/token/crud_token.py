from core.base_crud import CRUDBase
from .schemas import TokenCreate, TokenUpdate
from .models import Token
from sqlalchemy.orm.session import Session


class CRUDToken(CRUDBase[Token, TokenCreate, TokenUpdate]):
	
	def create(self, db: Session, *, obj_in: TokenCreate) -> Token:
		db_obj = Token(
				jwt=obj_in.jwt,
				user_id=obj_in.user_id,
		)
		
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj


init_token = CRUDToken(Token)
