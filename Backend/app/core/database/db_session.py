from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from core.base_settings import settings

engine = create_engine(
		url=settings.SQLALCHEMY_DATABASE_URI,
		pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
