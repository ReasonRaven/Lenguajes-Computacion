from typing import Annotated, Callable

from fastapi import APIRouter, Body

from core import explicaciones, greedy_search, star_search
from schemas import EJEMPLOS, BusquedaRequest, BusquedaResponse

router = APIRouter(prefix="/search", tags=["Módulo 2 · Logística y optimización"])

Peticion = Annotated[BusquedaRequest, Body(openapi_examples=EJEMPLOS)]

_RESPUESTAS = {
    422: {
        "description": "Entrada inválida: formato de grafo, pesos negativos, origen/destino "
        "inexistente o heurística euclidiana sin coordenadas."
    }
}


def _buscar(body: BusquedaRequest, clave: str, algoritmo: Callable[..., dict]) -> dict:
    h, heuristica = body.calcular_heuristica()
    resultado = algoritmo(body.grafo, body.origen, body.destino, h, body.limite_nodos)
    return {
        **resultado,
        "heuristica": heuristica,
        "origen": body.origen,
        "destino": body.destino,
        "limite_nodos": body.limite_nodos,
        "explicacion": explicaciones.algoritmo_grafo(clave, resultado, heuristica),
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
    return _buscar(body, "greedy", greedy_search.busqueda_voraz)


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
    return _buscar(body, "astar", star_search.busqueda_estrella)
