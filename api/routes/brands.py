from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from uuid import UUID

from api.db.session import get_session
from api.db.models.brand import Brand
from api.schemas.brand import BrandCreate, BrandUpdate, BrandOut, BrandListOut

router = APIRouter()

def _uuid_or_404(brand_id: str) -> UUID:
    try:
        return UUID(brand_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")

@router.post("", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
async def create_brand_endpoint(
    payload: BrandCreate,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    brand = Brand(
        brand_name=payload.brand_name,
        status=payload.status or "active",
    )
    session.add(brand)
    try:
        # aseguramos PK y valores por defecto antes de commit
        await session.flush()
        await session.refresh(brand)
        await session.commit()
    except sa.exc.IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="brand_name ya existe")
    return BrandOut.model_validate(brand)

@router.get("/{brand_id}", response_model=BrandOut)
async def get_brand_endpoint(
    brand_id: str,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    uid = _uuid_or_404(brand_id)
    brand = await session.get(Brand, uid)
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
    filters = []
    if q:
        filters.append(Brand.brand_name.ilike(f"%{q}%"))

    # total
    total = await session.scalar(
        sa.select(sa.func.count(Brand.id)).where(*filters)  # pylint: disable=not-callable
    )

    # items
    items = await session.scalars(
        sa.select(Brand)
        .where(*filters)
        .order_by(Brand.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = items.all()

    return BrandListOut(
        total=total or 0,
        items=[BrandOut.model_validate(b) for b in rows],
    )

@router.put("/{brand_id}", response_model=BrandOut)
async def update_brand_endpoint(
    brand_id: str,
    payload: BrandUpdate,
    session: AsyncSession = Depends(get_session),
) -> BrandOut:
    uid = _uuid_or_404(brand_id)
    brand = await session.get(Brand, uid)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")

    data = payload.model_dump(exclude_none=True)
    if "brand_name" in data:
        brand.brand_name = data["brand_name"]
    if "status" in data:
        brand.status = data["status"]

    try:
        # updated_at desde DB
        brand.updated_at = sa.func.now()  # pylint: disable=not-callable
        await session.flush()
        await session.refresh(brand)
        await session.commit()
    except sa.exc.IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de brand_name")
    return BrandOut.model_validate(brand)

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand_endpoint(
    brand_id: str,
    session: AsyncSession = Depends(get_session),
) -> None:
    uid = _uuid_or_404(brand_id)
    res = await session.execute(
        sa.delete(Brand).where(Brand.id == uid).returning(Brand.id)
    )
    deleted = res.scalar_one_or_none()
    if deleted is None:
        # no hubo cambios
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marca no encontrada")
    await session.commit()
    return None
