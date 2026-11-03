"""Modelo de la tabla productos."""

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class ProductoModel(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO 2: agrega las columnas sku, nombre, precio, existencias y categoria.
    sku: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    existencias: Mapped[int] = mapped_column(Integer, default=0)
    categoria: Mapped[str] = mapped_column(String(20), nullable=False)

    @property
    def disponible(self) -> bool:
        return self.existencias > 0
