from fastapi import APIRouter, Header, HTTPException

from app.services import ofertas, repartidores

router = APIRouter(prefix="/api/ofertas", tags=["ofertas"])


def _rid(authorization: str | None) -> str:
    token = (authorization or "").removeprefix("Bearer ").strip()
    try:
        return repartidores.repartidor_de_sesion(token)
    except repartidores.AccesoInvalido as e:
        raise HTTPException(401, str(e))


@router.get("")
def listar(repartidor_id: str, desde: float | None = None) -> list[dict]:
    try:
        return ofertas.ofertas_para(repartidor_id, desde=desde)
    except repartidores.NoEncontrado:
        raise HTTPException(404, "repartidor no encontrado")


def _cambio(fn, oid: str, authorization: str | None) -> dict:
    rid = _rid(authorization)
    try:
        return fn(oid, rid)
    except ofertas.NoEncontrada:
        raise HTTPException(404, "oferta no encontrada")
    except ofertas.TransicionInvalida as e:
        raise HTTPException(409, str(e))


@router.post("/{oid}/tomar")
def tomar(oid: str, authorization: str | None = Header(None)) -> dict:
    return _cambio(ofertas.tomar, oid, authorization)


@router.post("/{oid}/completar")
def completar(oid: str, authorization: str | None = Header(None)) -> dict:
    return _cambio(ofertas.completar, oid, authorization)
