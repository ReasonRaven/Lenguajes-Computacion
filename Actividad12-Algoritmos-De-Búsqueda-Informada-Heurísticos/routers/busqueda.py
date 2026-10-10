from typing import Annotated, Callable

from fastapi import APIRouter, Body

from core import grafos, greedy_search, star_search
from schemas import EJEMPLOS, BusquedaRequest, BusquedaResponse

router = APIRouter(prefix="/search", tags=["Búsqueda informada"])

Peticion = Annotated[BusquedaRequest, Body(openapi_examples=EJEMPLOS)]

_RESPUESTAS = {
    422: {
        "description": "Entrada inválida: formato de grafo, pesos negativos, origen/destino "
        "inexistente o heurística euclidiana sin coordenadas."
    }
}


def _heuristica(body: BusquedaRequest) -> tuple[dict[str, float], dict]:
    if body.heuristica == "euclidiana":
        h, k = grafos.heuristica_euclidiana(body.grafo, body.coordenadas, body.destino)
        formula = f"h(n) = {k:.4g} · distancia_euclidiana(n, {body.destino})"
    else:
        h, k = grafos.heuristica_saltos(body.grafo, body.destino)
        formula = f"h(n) = {k:g} · saltos(n, {body.destino})"
    return h, {"tipo": body.heuristica, "formula": formula, "escala": round(k, 6)}


def _buscar(body: BusquedaRequest, algoritmo: Callable[..., dict]) -> dict:
    h, heuristica = _heuristica(body)
    resultado = algoritmo(body.grafo, body.origen, body.destino, h, body.limite_nodos)
    return {
        **resultado,
        "heuristica": heuristica,
        "origen": body.origen,
        "destino": body.destino,
        "limite_nodos": body.limite_nodos,
    }


@router.post(
    "/greedy",
    summary="Búsqueda voraz (Greedy Best-First)",
    response_model=BusquedaResponse,
    responses=_RESPUESTAS,
)
def greedy(body: Peticion) -> dict:
    """Expande siempre el nodo de la frontera con menor **h(n)**, el que la heurística
    estima más cercano al destino (`f(n) = h(n)`). Es rápida, pero no garantiza la ruta
    de menor costo."""
    return _buscar(body, greedy_search.busqueda_voraz)


@router.post(
    "/star",
    summary="Búsqueda A*",
    response_model=BusquedaResponse,
    responses=_RESPUESTAS,
)
def star(body: Peticion) -> dict:
    """Expande siempre el nodo de la frontera con menor **f(n) = g(n) + h(n)**: costo
    acumulado más la estimación de lo que falta. Con una heurística admisible devuelve
    la ruta de menor costo."""
    return _buscar(body, star_search.busqueda_estrella)
