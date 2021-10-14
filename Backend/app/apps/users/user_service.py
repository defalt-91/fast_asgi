from apps.users.schemas import User, UserCreate
from services.db_service import get_db
from sqlalchemy.orm.session import Session
from fastapi import Depends, HTTPException, status
from apps.users.crud_user import user


async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
	conflict_username = user.get_user_by_username(db=db, username=user_in.username)
	if user_in.email:
		conflict_email = user.get_user_by_email(db=db, email=user_in.email)
		if conflict_email:
			raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="The user with this email already exists in the system.",
			)
	if conflict_username:
		raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="The user with this username already exists in the system.",
		)
	user_in_db = user.create(db=db, obj_in=user_in)
	return user_in_db
