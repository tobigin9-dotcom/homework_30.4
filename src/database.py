from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./cookbook.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей базы данных."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Создаёт асинхронную сессию базы данных.

    Yields:
        AsyncSession: асинхронная SQLAlchemy-сессия.
    """
    async with async_session_maker() as session:
        yield session
