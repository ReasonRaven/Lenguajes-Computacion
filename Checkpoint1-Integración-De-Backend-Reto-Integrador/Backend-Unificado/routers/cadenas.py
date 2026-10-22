from fastapi import APIRouter
from pydantic import BaseModel

from core import cadenas_ops, explicaciones

router = APIRouter(prefix="/cadenas", tags=["Módulo 1 · Lenguajes y autómatas"])


class ConcatenarRequest(BaseModel):
    a: str
    b: str


class UnirRequest(BaseModel):
    cadenas: list[str]


class PotenciaRequest(BaseModel):
    cadena: str
    n: int


@router.post("/concatenar")
def concatenar(body: ConcatenarRequest) -> dict:
    resultado = cadenas_ops.concatenar(body.a, body.b)
    return {
        "resultado": resultado,
        **explicaciones.cadena("concatenar", resultado, a=body.a, b=body.b),
    }


@router.post("/unir")
def unir(body: UnirRequest) -> dict:
    resultado = cadenas_ops.unir(body.cadenas)
    return {
        "resultado": resultado,
        **explicaciones.cadena("unir", resultado, cadenas=body.cadenas),
    }


@router.post("/potencia")
def potencia(body: PotenciaRequest) -> dict:
    resultado = cadenas_ops.potencia(body.cadena, body.n)
    return {
        "resultado": resultado,
        **explicaciones.cadena("potencia", resultado, cadena=body.cadena, n=body.n),
    }
