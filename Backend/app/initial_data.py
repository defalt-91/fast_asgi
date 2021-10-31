import logging

from core.database.session import SessionLocal

from services.init_db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
	db = SessionLocal()
	init_db(db)


def main() -> None:
	logger.info("Creating initial data")
	init()
	logger.info("Initial data created")


if __name__ == "__main__":
	main()
