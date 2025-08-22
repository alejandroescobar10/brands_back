from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from api.core.config import settings

ASYNC_URL = settings.database_url

# Fuerza psycopg3 (corrige lo que venga del .env)
if ASYNC_URL.startswith("postgresql+asyncpg://"):
    ASYNC_URL = ASYNC_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
elif ASYNC_URL.startswith("postgresql://"):
    ASYNC_URL = ASYNC_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_async_engine(
    ASYNC_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},  # Neon
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
