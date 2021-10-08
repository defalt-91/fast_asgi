from .schemas import User


class UserInDB(User):
    hashed_password: str