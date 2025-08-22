import sys, asyncio
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # frontend local
        # "https://tu-front.vercel.app",  # (añade cuando despliegues el front)
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        #await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.run_sync(Base.metadata.create_all)
@app.get("/api/health")
async def health():
    return {"ok": True}

app.include_router(brands_router, prefix="/api/brands", tags=["brands"])
