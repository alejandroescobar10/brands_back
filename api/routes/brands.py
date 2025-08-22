from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError  # <- para capturar UNIQUE, etc.

from api.db.session import get_session
from api.schemas.brand import BrandCreate, BrandUpdate, BrandOut, BrandListOut
from api.repositories.brands_repo import (
    create_brand,
    get_brand_by_id,
    list_brands,
    update_brand,
    delete_brand,
)

router = APIRouter()


@router.post("", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
async def create_brand_endpoint(
    payload: BrandCreate,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    """
    Crea una marca y devuelve el registro creado.

    201 Created: éxito
    409 Conflict: brand_name duplicado (UNIQUE)
    422 Unprocessable Entity: validación de payload
    """
    try:
        brand = await create_brand(session, payload)
        # Hint REST: ubicación del nuevo recurso
        response.headers["Location"] = f"/api/brands/{brand.id}"
        return brand
    except IntegrityError:
        # El repo ya hace rollback; aquí solo mapeamos a HTTP
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="brand_name ya existe",
        )


@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand_endpoint(
    brand_id: str,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    """
    Obtiene una marca por ID.
    404 si no existe.
    """
    brand = await get_brand_by_id(session, brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    # El repo puede devolver Brand (ORM) o BrandOut; normalizamos:
    return brand if isinstance(brand, BrandOut) else BrandOut.model_validate(brand)


@router.get("", response_model=BrandListOut)
async def list_brands_endpoint(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    q: str | None = None,
    session: AsyncSession = Depends(get_session),
) -> BrandListOut:
    """
    Lista marcas con paginación y filtro por nombre (q).
    """
    return await list_brands(session, limit, offset, q)


@router.put("/{brand_id}", response_model=BrandOut)
async def update_brand_endpoint(
    brand_id: str,
    payload: BrandUpdate,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    """
    Actualiza parcialmente una marca.
    404 si no existe.
    409 si brand_name entra en conflicto (UNIQUE).
    """
    try:
        updated = await update_brand(session, brand_id, payload)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
        return updated if isinstance(updated, BrandOut) else BrandOut.model_validate(updated)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de brand_name")


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_endpoint(
    brand_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Elimina una marca por ID.
    204 No Content si borra.
    404 si no existe.
    """
    ok = await delete_brand(session, brand_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    return None
