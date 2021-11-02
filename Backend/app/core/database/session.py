from psycopg2 import DataError
from sqlalchemy.orm.session import Session, sessionmaker
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
SessionLocal = sessionmaker(
    bind=engine, autoflush=True, autocommit=False, future=True, expire_on_commit=False
)
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    future=True,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
ScopedSessionLocal = ScopedSession(session_factory=SessionLocal)
AsyncScopedSession = async_scoped_session(
    session_factory=async_session_factory, scopefunc=current_task
)


def get_session() -> Generator:
    session: Session = SessionLocal()
    try:
        yield session
    except DataError:
        raise errors.session_error
    finally:
        session.close()


def get_scoped_session() -> Generator:
    session = ScopedSessionLocal()
    try:
        yield session
    except DataError:
        raise errors.session_error
    finally:
        session.close()


async def get_async_session() -> Generator:
    sa_session: AsyncSession = async_session_factory()
    try:
        yield sa_session
    finally:
        await sa_session.close()


async def scoped_async_session() -> Generator:
    sa_session: AsyncSession = AsyncScopedSession()
    await sa_session.begin()
    try:
        yield sa_session
    finally:
        await sa_session.remove()


async def get_async_session_context_manager() -> Generator:
    async with async_session_factory() as async_session:
        async with async_session.begin():
            yield async_session
