from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.core.config import settings
from api.routes.brands import router as brands_router

app = FastAPI(title="Brands API", version="1.0.0")

# CORS – en prod, reemplaza * por tu dominio del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/api/health")
async def health() -> dict:
    """Endpoint de salud para uptime checks."""
    return {"ok": True}

# Prefijo /api/brands
app.include_router(brands_router, prefix="/api/brands", tags=["brands"])
