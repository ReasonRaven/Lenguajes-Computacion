from fastapi import APIRouter
from pydantic import BaseModel

from core import lenguajes_ops

router = APIRouter(prefix="/lenguajes", tags=["lenguajes"])


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


@router.post("/union")
def union(body: DosLenguajesRequest) -> dict[str, list[str]]:
    return {"resultado": lenguajes_ops.union(body.L, body.M)}


@router.post("/interseccion")
def interseccion(body: DosLenguajesRequest) -> dict[str, list[str]]:
    return {"resultado": lenguajes_ops.interseccion(body.L, body.M)}


@router.post("/diferencia")
def diferencia(body: DosLenguajesRequest) -> dict[str, list[str]]:
    return {"resultado": lenguajes_ops.diferencia(body.L, body.M)}


@router.post("/concatenacion")
def concatenacion(body: DosLenguajesRequest) -> dict[str, list[str]]:
    return {"resultado": lenguajes_ops.concatenacion(body.L, body.M)}


@router.post("/complemento")
def complemento(body: ComplementoRequest) -> dict[str, list[str]]:
    return {
        "resultado": lenguajes_ops.complemento(
            body.L, body.alfabeto, body.max_length
        )
    }


@router.post("/clausura_kleene")
def clausura_kleene(body: ClausuraKleeneRequest) -> dict[str, list[str]]:
    return {
        "resultado": lenguajes_ops.clausura_kleene(body.L, body.max_elementos)
    }
