from core.database.db_session import SessionLocal
from typing import Generator


def get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
