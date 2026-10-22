from fastapi import APIRouter
from pydantic import BaseModel

from core import explicaciones, lenguajes_ops

router = APIRouter(prefix="/lenguajes", tags=["Módulo 1 · Lenguajes y autómatas"])


class DosLenguajesRequest(BaseModel):
    L: list[str]
    M: list[str]


class ComplementoRequest(BaseModel):
    L: list[str]
    alfabeto: list[str]
    max_length: int


class ClausuraKleeneRequest(BaseModel):
    L: list[str]
    max_elementos: int = 8


def _responder(operacion: str, resultado: list[str], **datos) -> dict:
    return {
        "resultado": resultado,
        **explicaciones.lenguaje(operacion, resultado, **datos),
    }


@router.post("/union")
def union(body: DosLenguajesRequest) -> dict:
    resultado = lenguajes_ops.union(body.L, body.M)
    return _responder("union", resultado, L=body.L, M=body.M)


@router.post("/interseccion")
def interseccion(body: DosLenguajesRequest) -> dict:
    resultado = lenguajes_ops.interseccion(body.L, body.M)
    return _responder("interseccion", resultado, L=body.L, M=body.M)


@router.post("/diferencia")
def diferencia(body: DosLenguajesRequest) -> dict:
    resultado = lenguajes_ops.diferencia(body.L, body.M)
    return _responder("diferencia", resultado, L=body.L, M=body.M)


@router.post("/concatenacion")
def concatenacion(body: DosLenguajesRequest) -> dict:
    resultado = lenguajes_ops.concatenacion(body.L, body.M)
    return _responder("concatenacion", resultado, L=body.L, M=body.M)


@router.post("/complemento")
def complemento(body: ComplementoRequest) -> dict:
    resultado = lenguajes_ops.complemento(body.L, body.alfabeto, body.max_length)
    return _responder("complemento", resultado, L=body.L)


@router.post("/clausura_kleene")
def clausura_kleene(body: ClausuraKleeneRequest) -> dict:
    resultado = lenguajes_ops.clausura_kleene(body.L, body.max_elementos)
    return _responder("clausura_kleene", resultado, L=body.L)
