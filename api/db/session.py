from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from api.core.config import settings

# -----------------------------------------------------------------------------
# URL de conexión asíncrona
# -----------------------------------------------------------------------------
# Se obtiene de las variables de entorno (DATABASE_URL) vía settings.
# Ejemplo típico con asyncpg: 
#   postgresql+asyncpg://user:pass@host:port/dbname
ASYNC_URL = settings.database_url

# -----------------------------------------------------------------------------
# Normalización de la URL
# -----------------------------------------------------------------------------
# Forzamos el uso de psycopg3 como driver (psycopg >= 3.x).
# Esto evita inconsistencias si el .env trae "asyncpg" o "postgresql" a secas.
# - Si empieza con postgresql+asyncpg://  → lo cambiamos a postgresql+psycopg://
# - Si empieza con postgresql://          → lo cambiamos a postgresql+psycopg://
if ASYNC_URL.startswith("postgresql+asyncpg://"):
    ASYNC_URL = ASYNC_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
elif ASYNC_URL.startswith("postgresql://"):
    ASYNC_URL = ASYNC_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# -----------------------------------------------------------------------------
# Motor asíncrono (engine)
# -----------------------------------------------------------------------------
# - pool_pre_ping=True: valida la conexión antes de usarla (reabre si está caída).
# - connect_args={"sslmode": "require"}: obligatorio en Neon (Postgres en la nube).
engine = create_async_engine(
    ASYNC_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},  # 👈 evita problemas de SSL en Neon
)

# -----------------------------------------------------------------------------
# Fábrica de sesiones
# -----------------------------------------------------------------------------
# async_sessionmaker crea instancias de AsyncSession sobre el engine.
# - expire_on_commit=False: evita que los objetos se "invaliden" tras commit().
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# -----------------------------------------------------------------------------
# Dependencia para FastAPI
# -----------------------------------------------------------------------------
# Se usa en los endpoints con "Depends(get_session)".
# Entrega una sesión de base de datos por request y la cierra al terminar.
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
