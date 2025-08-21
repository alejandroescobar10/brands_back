from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class BrandBase(BaseModel):
    brand_name: str = Field(min_length=2, max_length=120)
    status: str = Field(default="active")

class BrandCreate(BrandBase):
    """Payload para crear marcas."""
    pass

class BrandUpdate(BaseModel):
    """Payload para actualizar marcas (PUT)."""
    brand_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    status: Optional[str] = Field(default=None)

class BrandOut(BrandBase):
    """Respuesta de una marca."""
    id: UUID
    class Config:
        from_attributes = True

class BrandListOut(BaseModel):
    """Respuesta paginada."""
    total: int
    items: list[BrandOut]
