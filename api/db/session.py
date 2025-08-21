from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from api.core.config import settings

# Engine async hacia Neon (psycopg + sslmode=require)
engine = create_async_engine(settings.database_url, pool_pre_ping=True)

SessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI: inyecta una sesión async y la cierra al terminar."""
    async with SessionFactory() as session:
        yield session
