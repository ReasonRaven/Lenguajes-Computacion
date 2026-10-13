from typing import Annotated, Callable

from fastapi import APIRouter, Body

from core import dijkstra, generador, metricas, tsp
from schemas import (
    EJEMPLOS_DIJKSTRA,
    EJEMPLOS_GENERAR,
    EJEMPLOS_TSP,
    AlgoritmoResponse,
    DijkstraRequest,
    GenerarRequest,
    GrafoGenerado,
    TSPExactoRequest,
    TSPRequest,
)

router = APIRouter(prefix="/graph", tags=["Algoritmos P, NP y con heurística"])

_RESPUESTAS = {
    422: {
        "description": "Entrada inválida: formato de grafo, pesos negativos, nodo "
        "inexistente o grafo demasiado grande para el TSP exacto."
    }
}


def _ejecutar(
    info: dict, algoritmo: Callable[..., dict], body, *args: str, destino: str | None = None
) -> dict:
    resultado, tiempo_ms, memoria_kb = metricas.medir(algoritmo, body.grafo, *args)
    return {
        **info,
        **resultado,
        "origen": body.origen,
        "destino": destino,
        "num_nodos": len(body.grafo),
        "tiempo_ms": tiempo_ms,
        "memoria_kb": memoria_kb,
    }


@router.post(
    "/dijkstra",
    summary="Dijkstra (camino de menor costo)",
    response_model=AlgoritmoResponse,
    responses=_RESPUESTAS,
)
def ruta_dijkstra(
    body: Annotated[DijkstraRequest, Body(openapi_examples=EJEMPLOS_DIJKSTRA)],
) -> dict:
    """Camino de menor costo entre `origen` y `destino`. Problema en **P**:
    `O((V + E) log V)` con cola de prioridad. Requiere pesos no negativos."""
    info = {
        "algoritmo": dijkstra.ALGORITMO,
        "clase": dijkstra.CLASE,
        "complejidad": dijkstra.COMPLEJIDAD,
    }
    return _ejecutar(
        info, dijkstra.dijkstra, body, body.origen, body.destino, destino=body.destino
    )


@router.post(
    "/tsp",
    summary="Agente viajero exacto (Held-Karp)",
    response_model=AlgoritmoResponse,
    responses=_RESPUESTAS,
)
def ruta_tsp(body: Annotated[TSPExactoRequest, Body(openapi_examples=EJEMPLOS_TSP)]) -> dict:
    """Ciclo de menor costo que visita todos los nodos una vez y regresa al
    origen. Problema **NP-difícil**: la programación dinámica de Held-Karp da el
    óptimo en `O(n² · 2ⁿ)`. Admite hasta 18 nodos."""
    return _ejecutar(tsp.EXACTO, tsp.tsp_exacto, body, body.origen)


@router.post(
    "/tsp/greedy",
    summary="Agente viajero con heurística voraz (vecino más cercano)",
    response_model=AlgoritmoResponse,
    responses=_RESPUESTAS,
)
def ruta_tsp_voraz(body: Annotated[TSPRequest, Body(openapi_examples=EJEMPLOS_TSP)]) -> dict:
    """Desde el nodo actual avanza siempre por la arista más barata hacia un nodo
    no visitado. `O(n²)`, sin garantía de óptimo; en grafos incompletos puede
    quedarse sin salida."""
    return _ejecutar(tsp.VORAZ, tsp.tsp_voraz, body, body.origen)


@router.post(
    "/generate",
    summary="Generar un grafo sintético ponderado",
    response_model=GrafoGenerado,
    responses={422: {"description": "Parámetros fuera de rango."}},
)
def generar(body: Annotated[GenerarRequest, Body(openapi_examples=EJEMPLOS_GENERAR)]) -> dict:
    """Genera un grafo conexo con un ciclo hamiltoniano garantizado más aristas
    aleatorias según `densidad`. La respuesta se puede enviar tal cual a los otros
    endpoints (agregando `origen`/`destino`)."""
    return generador.generar_grafo(**body.model_dump())
