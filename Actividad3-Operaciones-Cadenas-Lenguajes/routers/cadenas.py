from fastapi import APIRouter
from pydantic import BaseModel

from core import cadenas_ops

router = APIRouter(prefix="/cadenas", tags=["cadenas"])


class ConcatenarRequest(BaseModel):
    a: str
    b: str


class UnirRequest(BaseModel):
    cadenas: list[str]


class PotenciaRequest(BaseModel):
    cadena: str
    n: int


@router.post("/concatenar")
def concatenar(body: ConcatenarRequest) -> dict[str, str]:
    return {"resultado": cadenas_ops.concatenar(body.a, body.b)}


@router.post("/unir")
def unir(body: UnirRequest) -> dict[str, str]:
    return {"resultado": cadenas_ops.unir(body.cadenas)}


@router.post("/potencia")
def potencia(body: PotenciaRequest) -> dict[str, str]:
    return {"resultado": cadenas_ops.potencia(body.cadena, body.n)}
