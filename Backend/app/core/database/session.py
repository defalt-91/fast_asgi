import typing

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
	# echo=True,
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
		raise
	else:
		session.commit()
	finally:
		session.close()


class SessionContextManager:
	def __init__(self):
		self.session = SessionFactory()
	
	def __enter__(self):
		return self.session
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.session.close()


async def test_ctx():
	with SessionContextManager() as session:
		yield session


# async def get_async_session() -> Generator:
# 	async with AsyncSessionFactory() as async_session:
# 		return async_session
async def get_async_session() -> typing.Generator:
	session = AsyncSessionFactory()
	try:
		# print(session.connection())
		# print(session.get_transaction())
		yield session
	except:
		await session.rollback()
		raise
	else:
		print(engine.pool.status())
		print(engine.pool.status())
		await session.commit()
	finally:
		print(engine.pool.status())
		print(engine.pool.status())
		await session.close()


def get_scoped_session() -> Generator:
	with ScopedSessionLocal() as scoped_session:
		yield scoped_session


# verbose version of what a context manager will do
async def get_scoped_async_session() -> Generator:
	async with AsyncScopedSession().begin() as AsyncScoped_session:
		yield AsyncScoped_session
