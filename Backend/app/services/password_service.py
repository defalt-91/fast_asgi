from passlib.context import CryptContext

pwd_context = CryptContext(
		schemes=["bcrypt"],
		deprecated="auto"
)


def get_password_hash(password):
	return pwd_context.hash(
			password,
			# category="admin"
	)


def verify_password(plain_password, hashed_password):
	return pwd_context.verify(
			secret=plain_password,
			hash=hashed_password,
			category=None
	)
