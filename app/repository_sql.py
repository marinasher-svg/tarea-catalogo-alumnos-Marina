"""Repositorio del catálogo sobre SQLite. Misma interfaz que el de memoria."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import get_session
from .models import ProductoModel
from .repository import ExistenciasInsuficientes, SkuDuplicado
from .schemas import Categoria, ProductoIn, ProductoOut


class SqlProductoRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _guardar(self, producto: ProductoModel) -> ProductoOut:
        # TODO 3: haz commit. Si la BD lanza IntegrityError (SKU repetido),
        # haz rollback y lanza SkuDuplicado.
        try:
            self.session.commit()
            self.session.refresh(producto)
            return ProductoOut.model_validate(producto)
        except IntegrityError as error:
            self.session.rollback()
            raise SkuDuplicado() from error

    def add(self, data: ProductoIn) -> ProductoOut:
        producto = ProductoModel(**data.model_dump())
        self.session.add(producto)
        return self._guardar(producto)

    def list(
        self, categoria: Categoria | None = None, solo_disponibles: bool = False
    ) -> list[ProductoOut]:
        # TODO 4: arma un select(ProductoModel) ordenado por id y agrega .where()
        consulta = select(ProductoModel).order_by(ProductoModel.id)
        
        if categoria:
            consulta = consulta.where(ProductoModel.categoria == categoria.value)
            
        if solo_disponibles:
            consulta = consulta.where(ProductoModel.existencias > 0)
            
        resultado = self.session.scalars(consulta).all()
        return [ProductoOut.model_validate(p) for p in resultado]

    def get(self, producto_id: int) -> ProductoOut | None:
        producto = self.session.get(ProductoModel, producto_id)
        return ProductoOut.model_validate(producto) if producto else None

    def update(self, producto_id: int, data: ProductoIn) -> ProductoOut | None:
        # TODO 5: busca el producto; si no existe devuelve None.
        # Copia cada campo con setattr y guarda.
        producto = self.session.get(ProductoModel, producto_id)
        if producto is None:
            return None
            
        for campo, valor in data.model_dump().items():
            setattr(producto, campo, valor)
            
        return self._guardar(producto)

    def delete(self, producto_id: int) -> bool:
        producto = self.session.get(ProductoModel, producto_id)
        if producto is None:
            return False
        self.session.delete(producto)
        self.session.commit()
        return True

    def ajustar_existencias(self, producto_id: int, cantidad: int) -> ProductoOut | None:
        # TODO 6: igual que en la Práctica 3, pero sobre el modelo:
        producto = self.session.get(ProductoModel, producto_id)
        if producto is None:
            return None
            
        nueva_existencia = producto.existencias + cantidad
        if nueva_existencia < 0:
            raise ExistenciasInsuficientes()
            
        producto.existencias = nueva_existencia
        self.session.commit()
        self.session.refresh(producto)
        return ProductoOut.model_validate(producto)


def get_repo(session: Annotated[Session, Depends(get_session)]) -> SqlProductoRepository:
    return SqlProductoRepository(session)
