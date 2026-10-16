from typing import Annotated, Callable

from fastapi import APIRouter, Body

from core import (
    bfs,
    comparador,
    dfs,
    dijkstra,
    explicaciones,
    generador,
    hill_climbing,
    metricas,
    tsp,
)
from schemas import (
    EJEMPLOS_COMPARAR,
    EJEMPLOS_DIJKSTRA,
    EJEMPLOS_GENERAR,
    EJEMPLOS_HILL,
    EJEMPLOS_RECORRIDO,
    EJEMPLOS_TSP,
    AlgoritmoResponse,
    CompararRequest,
    CompararResponse,
    DijkstraRequest,
    GenerarRequest,
    GrafoGenerado,
    HillClimbingRequest,
    RecorridoRequest,
    TSPExactoRequest,
    TSPRequest,
)

router = APIRouter(prefix="/graph", tags=["Módulo 2 · Logística y optimización"])

_RESPUESTAS = {
    422: {
        "description": "Entrada inválida: formato de grafo, pesos negativos, nodo "
        "inexistente o grafo demasiado grande para el TSP exacto."
    }
}


def _info(modulo) -> dict:
    return {"algoritmo": modulo.ALGORITMO, "clase": modulo.CLASE, "complejidad": modulo.COMPLEJIDAD}


def _ejecutar(
    clave: str,
    info: dict,
    algoritmo: Callable[..., dict],
    body,
    *args,
    destino: str | None = None,
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
        "explicacion": explicaciones.algoritmo_grafo(clave, resultado),
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
    return _ejecutar(
        "dijkstra",
        _info(dijkstra),
        dijkstra.dijkstra,
        body,
        body.origen,
        body.destino,
        destino=body.destino,
    )


@router.post(
    "/bfs",
    summary="Búsqueda en anchura (BFS)",
    response_model=AlgoritmoResponse,
    responses=_RESPUESTAS,
)
def ruta_bfs(body: Annotated[RecorridoRequest, Body(openapi_examples=EJEMPLOS_RECORRIDO)]) -> dict:
    """Explora por niveles con una cola. Con `destino`, devuelve la ruta con **menos
    aristas**; sin `destino`, el **alcance máximo**: cada nodo alcanzable y a cuántos
    saltos está. `O(V + E)`."""
    return _ejecutar(
        "bfs", _info(bfs), bfs.bfs, body, body.origen, body.destino, destino=body.destino
    )


@router.post(
    "/dfs",
    summary="Búsqueda en profundidad (DFS)",
    response_model=AlgoritmoResponse,
    responses=_RESPUESTAS,
)
def ruta_dfs(body: Annotated[RecorridoRequest, Body(openapi_examples=EJEMPLOS_RECORRIDO)]) -> dict:
    """Avanza por una rama hasta el fondo y retrocede (pila). Con `destino`, devuelve
    la primera ruta que encuentra (no necesariamente la mejor); sin `destino`, el
    alcance máximo con la profundidad de cada nodo en el árbol DFS. `O(V + E)`."""
    return _ejecutar(
        "dfs", _info(dfs), dfs.dfs, body, body.origen, body.destino, destino=body.destino
    )


@router.post(
    "/hill-climbing",
    summary="Ascenso de colinas (Hill-Climbing)",
    response_model=AlgoritmoResponse,
    responses=_RESPUESTAS,
)
def ruta_hill_climbing(
    body: Annotated[HillClimbingRequest, Body(openapi_examples=EJEMPLOS_HILL)],
) -> dict:
    """Búsqueda local: desde el nodo actual se mueve al vecino con menor **h(n)**
    solo si mejora. Puede quedarse en un óptimo local sin llegar al destino."""
    h, heuristica = body.calcular_heuristica()
    respuesta = _ejecutar(
        "hill-climbing",
        _info(hill_climbing),
        hill_climbing.hill_climbing,
        body,
        body.origen,
        body.destino,
        h,
        destino=body.destino,
    )
    respuesta["explicacion"] = explicaciones.algoritmo_grafo(
        "hill-climbing", respuesta, heuristica
    )
    return respuesta


@router.post(
    "/compare",
    summary="Comparar algoritmos de ruta sobre el mismo grafo",
    response_model=CompararResponse,
    responses=_RESPUESTAS,
)
def comparar(body: Annotated[CompararRequest, Body(openapi_examples=EJEMPLOS_COMPARAR)]) -> dict:
    """Ejecuta los `algoritmos` elegidos (BFS, DFS, Hill-Climbing, voraz, A* y
    Dijkstra) con exactamente el mismo grafo, origen y destino, y devuelve una tabla
    comparativa: ruta, costo, nodos recorridos, tiempo y memoria."""
    usa_h = any(comparador.CATALOGO[a][3] for a in body.algoritmos)
    h, heuristica = body.calcular_heuristica() if usa_h else (None, None)
    resultado = comparador.comparar(body.grafo, body.origen, body.destino, h, body.algoritmos)
    return {
        "origen": body.origen,
        "destino": body.destino,
        "num_nodos": len(body.grafo),
        "heuristica": heuristica,
        **resultado,
        "explicacion": explicaciones.comparacion(resultado),
    }


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
    return _ejecutar("tsp", tsp.EXACTO, tsp.tsp_exacto, body, body.origen)


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
    return _ejecutar("tsp-greedy", tsp.VORAZ, tsp.tsp_voraz, body, body.origen)


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
    return {
        **generador.generar_grafo(**body.model_dump()),
        "explicacion": explicaciones.TEORIA["generar"],
    }
