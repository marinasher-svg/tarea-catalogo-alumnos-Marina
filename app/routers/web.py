"""Página HTML del catálogo: lista + formulario de alta."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from ..repository import SkuDuplicado
from ..repository_sql import SqlProductoRepository, get_repo
from ..schemas import Categoria, ProductoIn

router = APIRouter(prefix="/web", include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

Repo = Annotated[SqlProductoRepository, Depends(get_repo)]


def _pagina(request: Request, repo: SqlProductoRepository, datos, errores, status_code=200):
    contexto = {
        "productos": repo.list(),
        "categorias": list(Categoria),
        "datos": datos,
        "errores": errores,
    }
    return templates.TemplateResponse(request, "catalogo.html", contexto, status_code=status_code)


@router.get("/productos", response_class=HTMLResponse)
def catalogo(request: Request, repo: Repo):
    return _pagina(request, repo, datos={}, errores={})


# TODO 7: POST /web/productos que reciba sku, nombre, precio, existencias y categoria
@router.post("/productos", response_class=HTMLResponse)
def crear_producto_desde_formulario(
    request: Request,
    repo: Repo,
    sku: Annotated[str, Form()] = "",
    nombre: Annotated[str, Form()] = "",
    precio: Annotated[str, Form()] = "",
    existencias: Annotated[str, Form()] = "",
    categoria: Annotated[str, Form()] = "",
):
    datos = {
        "sku": sku,
        "nombre": nombre,
        "precio": precio,
        "existencias": existencias,
        "categoria": categoria,
    }
    
    try:
        producto_validado = ProductoIn(**datos)
        repo.add(producto_validado)
    except ValidationError as error:
        errores = {e["loc"][0]: e["msg"] for e in error.errors()}
        return _pagina(request, repo, datos=datos, errores=errores, status_code=422)
    except SkuDuplicado:
        errores = {"general": "El SKU ya existe"}
        return _pagina(request, repo, datos=datos, errores=errores, status_code=409)
        
    return RedirectResponse("/web/productos", status_code=303)
