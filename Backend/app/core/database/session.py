from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import (
	AsyncSession,
	create_async_engine,
	async_scoped_session,
)
from core.base_settings import settings
from typing import Generator
from sqlalchemy.orm.scoping import ScopedSession
from services import errors
from asyncio import current_task


engine = create_engine(
	url=settings.SQLALCHEMY_DATABASE_URI,
	pool_pre_ping=True,
	echo=True,
	future=True,
)
async_engine = create_async_engine(
	url=settings.SQLALCHEMY_ASYNC_DATABASE_URI,
	pool_pre_ping=True,
	echo=True,
	future=True,
)
SessionFactory = sessionmaker(
	bind=engine,
	future=True,
	autoflush=True,
	autocommit=False,
	expire_on_commit=False
)
AsyncSessionFactory = sessionmaker(
	bind=async_engine,
	class_=AsyncSession,
	future=True,
	autoflush=True,
	autocommit=False,
	expire_on_commit=False,
)
ScopedSessionLocal = ScopedSession(session_factory=SessionFactory)
AsyncScopedSession = async_scoped_session(session_factory=AsyncSessionFactory, scopefunc=current_task)


def get_session() -> Generator:
	session = SessionFactory()
	try:
		yield session
	except:
		session.rollback()
		raise ConnectionError
	# else:
	# 	session.commit()
	finally:
		session.close()


async def get_async_session() -> Generator:
	async with AsyncSessionFactory().begin() as async_session:
		yield async_session


def get_scoped_session() -> Generator:
	with ScopedSessionLocal().begin() as scoped_session:
		yield scoped_session


# verbose version of what a context manager will do
async def get_scoped_async_session() -> Generator:
	async with AsyncScopedSession().begin() as AsyncScoped_session:
		yield AsyncScoped_session
