import sys, asyncio
# En Windows, FastAPI/uvicorn con asyncio a veces requiere esta política
# para evitar problemas con selectores de I/O. En Linux/macOS no es necesario.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import sqlalchemy as sa
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.routes.brands import router as brands_router

from api.db.base import Base
from api.db.session import engine  # ← usa el engine async
import api.db.models.brand         # ← importa modelos

app = FastAPI(title="Brands API", version="1.0.0")
# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
# Habilita orígenes permitidos para que el frontend pueda llamar al backend
# - En local: Vite corre en http://localhost:5173
# - En producción: agrega el dominio real del frontend de Vercel (https)
# IMPORTANTE:
#   - Si allow_credentials=True, NO usar "*" como origen.
#   - Para cubrir "previews" de Vercel, puedes usar allow_origin_regex (ver ejemplo abajo).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # frontend local
        "https://brands-front.vercel.app",  # frontend en Vercel
    ],
    # allow_origin_regex=r"https://.*\.vercel\.app$",  # <- (Opcional) habilita previews de Vercel
    allow_methods=["*"],               # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],               # Permite todos los headers (Authorization, Content-Type, etc.)
    allow_credentials=True,            # Si usas cookies/sesión; si no, puedes poner False
)

# -----------------------------------------------------------------------------
# Eventos de ciclo de vida
# -----------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        #await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.run_sync(Base.metadata.create_all)
        
# -----------------------------------------------------------------------------
# Endpoints base / healthcheck
# -----------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"ok": True}
# -----------------------------------------------------------------------------
# Rutas del módulo "brands"
# -----------------------------------------------------------------------------
# Agrupa las rutas de marcas bajo /api/brands, con etiqueta "brands"
# Ejemplos:
#   GET  /api/brands
#   POST /api/brands
#   GET  /api/brands/{id}
#   PUT  /api/brands/{id}
#   DELETE /api/brands/{id}
app.include_router(brands_router, prefix="/api/brands", tags=["brands"])
