from fastapi import APIRouter

from app.services.crecimiento import Crecimiento, crecimiento

router = APIRouter(prefix="/api/sedeco", tags=["crecimiento"])


@router.get("/crecimiento", response_model=Crecimiento)
def get_crecimiento() -> Crecimiento:
    return crecimiento()
