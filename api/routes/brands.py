from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.session import get_session
from api.repositories.brands_repo import (
    create_brand, get_brand_by_id, list_brands, update_brand, delete_brand
)
from api.schemas.brand import BrandCreate, BrandUpdate, BrandOut, BrandListOut

router = APIRouter()

@router.post("", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
async def create_brand_endpoint(
    payload: BrandCreate,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    """Endpoint: crea una marca y devuelve el registro creado."""
    try:
        return await create_brand(session, payload)
    except Exception:
        # conflicto de unique brand_name u otro error de integridad
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="brand_name ya existe")

@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand_endpoint(
    brand_id: str,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    """Endpoint: devuelve una marca por su ID, 404 si no existe."""
    brand = await get_brand_by_id(session, brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    return BrandOut.model_validate(brand)

@router.get("", response_model=BrandListOut)
async def list_brands_endpoint(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> BrandListOut:
    """Endpoint: lista marcas con paginación y búsqueda."""
    return await list_brands(session, limit, offset, q)

@router.put("/{brand_id}", response_model=BrandOut)
async def update_brand_endpoint(
    brand_id: str,
    payload: BrandUpdate,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    """Endpoint: actualiza una marca. 404 si no existe; 409 si hay conflicto."""
    try:
        updated = await update_brand(session, brand_id, payload)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
        return updated
    except Exception:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de brand_name")

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_endpoint(
    brand_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Endpoint: elimina una marca por ID. 404 si no existe."""
    ok = await delete_brand(session, brand_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    return None
