from typing import Any

from fastapi import HTTPException, Depends, Query, Body

from apps.users import crud_user
from services.db_service import get_db
from services.email_service import generate_password_reset_token, send_reset_password_email, verify_password_reset_token
from sqlalchemy.orm import Session
from pydantic import EmailStr

from services.password_service import get_password_hash


async def password_recover(
	email: EmailStr = Query(...),
	db: Session = Depends(get_db),
):
	""" Password Recovery """
	user = crud_user.user.get_user_by_email(db, email=email)
	if not user:
		raise HTTPException(status_code=404, detail="The user with this email does not exist in the system.")
	password_reset_token = generate_password_reset_token(email=email)
	send_reset_password_email(
		email_to=user.email,
		username=user.username,
		token=password_reset_token
	)
	return {"msg": "Password recovery email sent"}


def reset_password(
	token: str = Body(...),
	new_password: str = Body(...),
	db: Session = Depends(get_db),
) -> Any:
	""" Reset password """
	email = verify_password_reset_token(token)
	if not email:
		raise HTTPException(status_code=400, detail="Invalid token")
	user = crud_user.user.get_user_by_email(db, email=email)
	if not user:
		raise HTTPException(
			status_code=404,
			detail="The user with this username does not exist in the system.",
		)
	elif not crud_user.user.is_active(user):
		raise HTTPException(status_code=400, detail="Inactive user")
	hashed_password = get_password_hash(new_password)
	user.hashed_password = hashed_password
	db.add(user)
	db.commit()
	return {"msg": "Password updated successfully"}
