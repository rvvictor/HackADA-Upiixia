from fastapi import APIRouter

from app.services import repartidores

router = APIRouter(prefix="/api/incentivos", tags=["incentivos"])


@router.get("")
def listar() -> list[dict]:
    return repartidores.incentivos()
