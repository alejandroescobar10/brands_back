from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from uuid import UUID

class BrandBase(BaseModel):
    brand_name: str = Field(min_length=2, max_length=120, strip_whitespace=True)
    titular: Optional[str] = Field(default=None, min_length=2, max_length=120)
    status: Literal["active", "inactive", "draft"] = Field(default="active")
    

class BrandCreate(BrandBase):
    """Payload para crear marcas."""
    pass

class BrandUpdate(BaseModel):
    """Payload para actualizar marcas (PUT/PATCH)."""
    brand_name: Optional[str] = Field(default=None, min_length=2, max_length=120, strip_whitespace=True)
    titular: Optional[str] = Field(default=None, min_length=2, max_length=120)
    status: Optional[Literal["active", "inactive", "draft"]] = None
    

class BrandOut(BrandBase):
    """Respuesta de una marca."""
    id: UUID
    # Pydantic v2: permite construir desde objetos ORM (antes: orm_mode)
    model_config = ConfigDict(from_attributes=True)

class BrandListOut(BaseModel):
    """Respuesta paginada."""
    total: int
    items: list[BrandOut]
