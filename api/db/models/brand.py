from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TIMESTAMP
from api.db.base import Base

class Brand(Base):
    """Modelo de la tabla brands."""
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    brand_name = Column(String(120), nullable=False, unique=True, index=True)
    status = Column(String(16), nullable=False, server_default=text("'active'"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
    