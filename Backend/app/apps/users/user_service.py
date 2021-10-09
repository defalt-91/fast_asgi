from apps.users.schemas import User, UserCreate
from services.db_service import get_db
from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException, status
from apps.users.crud_user import user


async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
	conflict_user = user.get_user_by_email(db=db, email=user_in.email)
	if conflict_user:
		raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="The user with this email already exists in the system.",
		)
	user_in_db = user.create(db=db, obj_in=user_in)
	return user_in_db
