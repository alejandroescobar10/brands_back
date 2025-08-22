from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.brand import Brand
from api.schemas.brand import BrandCreate, BrandUpdate, BrandOut, BrandListOut

async def create_brand(session: AsyncSession, payload: BrandCreate) -> BrandOut:
    """
    Inserta una nueva marca.
    Lanza IntegrityError si brand_name viola UNIQUE.
    """
    brand = Brand(brand_name=payload.brand_name, status=payload.status, titular=payload.titular,)
    session.add(brand)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise
    await session.refresh(brand)
    return BrandOut.model_validate(brand)

async def get_brand_by_id(session: AsyncSession, brand_id: str) -> Brand | None:
    """
    Retorna la marca por ID, o None si no existe.
    """
    res = await session.execute(select(Brand).where(Brand.id == brand_id))
    return res.scalar_one_or_none()

async def list_brands(
    session: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    q: str | None = None,
) -> BrandListOut:
    """
    Lista marcas con paginación y filtro opcional por nombre (ilike).
    """
    stmt = select(Brand)
    if q:
        stmt = stmt.where(Brand.brand_name.ilike(f"%{q}%"))

    # total usando subquery para no contar toda la tabla sin filtros
    total = (
        await session.execute(
            select(func.count()).select_from(stmt.subquery())
        )
    ).scalar_one()

    rows = (
        await session.execute(
            stmt.order_by(Brand.created_at.desc()).limit(limit).offset(offset)
        )
    ).scalars().all()

    return BrandListOut(total=total, items=[BrandOut.model_validate(b) for b in rows])

async def update_brand(session: AsyncSession, brand_id: str, payload: BrandUpdate) -> BrandOut | None:
    """
    Actualiza campos parciales de una marca. Retorna None si no existe.
    Lanza IntegrityError si brand_name choca con UNIQUE.
    """
    values = payload.model_dump(exclude_none=True)
    if not values:
        # nada que actualizar: devuelve estado actual (si existe)
        res = await session.execute(select(Brand).where(Brand.id == brand_id))
        obj = res.scalar_one_or_none()
        return BrandOut.model_validate(obj) if obj else None

    values["updated_at"] = func.now()

    try:
        res = await session.execute(
            update(Brand)
            .where(Brand.id == brand_id)
            .values(**values)
            .returning(Brand)
        )
        row = res.scalar_one_or_none()
        if not row:
            await session.rollback()
            return None
        await session.commit()
        return BrandOut.model_validate(row)
    except IntegrityError:
        await session.rollback()
        raise

async def delete_brand(session: AsyncSession, brand_id: str) -> bool:
    """
    Elimina por ID. Retorna True si borró, False si no existía.
    """
    res = await session.execute(
        delete(Brand).where(Brand.id == brand_id).returning(Brand.id)
    )
    deleted = res.scalar_one_or_none()
    if deleted:
        await session.commit()
        return True
    await session.rollback()
    return False
