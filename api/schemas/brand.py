from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from uuid import UUID

# -----------------------------------------------------------------------------
# Base de todos los esquemas de Marca
# -----------------------------------------------------------------------------
# Incluye los campos comunes a create, update y output.
# -----------------------------------------------------------------------------
class BrandBase(BaseModel):
    # Nombre de la marca (obligatorio, entre 2 y 120 caracteres).
    brand_name: str = Field(min_length=2, max_length=120, strip_whitespace=True)

    # Titular de la marca (opcional, pero si viene debe tener entre 2 y 120 caracteres).
    titular: Optional[str] = Field(default=None, min_length=2, max_length=120)

    # Estado de la marca. Valores restringidos (Literal).
    # Por defecto se crea como "active".
    status: Literal["active", "inactive", "draft"] = Field(default="active")


# -----------------------------------------------------------------------------
# Esquema para creación
# -----------------------------------------------------------------------------
# Hereda de BrandBase, no agrega nada nuevo, pero semánticamente se usa
# para distinguir el payload de creación.
# -----------------------------------------------------------------------------
class BrandCreate(BrandBase):
    """Payload para crear marcas."""
    pass


# -----------------------------------------------------------------------------
# Esquema para actualización
# -----------------------------------------------------------------------------
# Se diferencia porque todos los campos son opcionales (permiten actualizar
# solo un subconjunto de atributos).
# -----------------------------------------------------------------------------
class BrandUpdate(BaseModel):
    """Payload para actualizar marcas (PUT/PATCH)."""
    brand_name: Optional[str] = Field(
        default=None, min_length=2, max_length=120, strip_whitespace=True
    )
    titular: Optional[str] = Field(
        default=None, min_length=2, max_length=120
    )
    status: Optional[Literal["active", "inactive", "draft"]] = None


# -----------------------------------------------------------------------------
# Esquema de salida (respuesta de la API)
# -----------------------------------------------------------------------------
# Incluye el ID (UUID) además de los campos base.
# ConfigDict(from_attributes=True) permite construir este modelo
# directamente desde objetos ORM (como los de SQLAlchemy).
# -----------------------------------------------------------------------------
class BrandOut(BrandBase):
    """Respuesta de una marca."""
    id: UUID
    model_config = ConfigDict(from_attributes=True)


# -----------------------------------------------------------------------------
# Esquema de salida paginada
# -----------------------------------------------------------------------------
# Contiene total de registros y una lista de marcas (BrandOut).
# Útil para listados con paginación.
# -----------------------------------------------------------------------------
class BrandListOut(BaseModel):
    """Respuesta paginada."""
    total: int
    items: list[BrandOut]
