"""Comparación de algoritmos de ruta sobre el mismo grafo.

Cada algoritmo elegido se ejecuta con exactamente la misma entrada (grafo,
origen, destino y heurística) y se mide con `metricas.medir`, para poder
compararlos en una tabla: ruta, costo, nodos recorridos, tiempo y memoria.
"""

from typing import Callable

from core import bfs, dfs, dijkstra, grafos, greedy_search, hill_climbing, metricas, star_search

# clave -> (nombre, clase, complejidad, ¿usa heurística?, ¿requiere destino?)
CATALOGO: dict[str, tuple[str, str, str, bool, bool]] = {
    "bfs": (bfs.ALGORITMO, bfs.CLASE, bfs.COMPLEJIDAD, False, False),
    "dfs": (dfs.ALGORITMO, dfs.CLASE, dfs.COMPLEJIDAD, False, False),
    "hill-climbing": (
        hill_climbing.ALGORITMO,
        hill_climbing.CLASE,
        hill_climbing.COMPLEJIDAD,
        True,
        True,
    ),
    "greedy": (greedy_search.ALGORITMO, "Heurística (búsqueda informada)", "O(b^m)", True, True),
    "astar": (star_search.ALGORITMO, "P (con heurística admisible da el óptimo)", "O(b^d)", True, True),
    "dijkstra": (dijkstra.ALGORITMO, dijkstra.CLASE, dijkstra.COMPLEJIDAD, False, True),
}

REQUIEREN_DESTINO = [clave for clave, info in CATALOGO.items() if info[4]]


def _informada(algoritmo: Callable[..., dict]) -> Callable[..., dict]:
    """Adapta la búsqueda voraz / A* (que llevan traza y T(n)/S(n)) a las
    llaves de la tabla. Sin límite de nodos, para compararlas en igualdad."""

    def ejecutar(grafo, origen, destino, h):
        r = algoritmo(grafo, origen, destino, h, len(grafo))
        return {
            "solucion": r["solucion"],
            "ruta": r["ruta"],
            "costo": r["costo"],
            "nodos_recorridos": r["nodos_visitados"],
            "operaciones": r["T(n)"]["nodos_generados"],
            "orden_visita": [paso["nodo"] for paso in r["traza"]],
            "motivo": r["motivo"],
        }

    return ejecutar


_FUNCIONES: dict[str, Callable[..., dict]] = {
    "bfs": lambda g, o, d, h: bfs.bfs(g, o, d),
    "dfs": lambda g, o, d, h: dfs.dfs(g, o, d),
    "hill-climbing": hill_climbing.hill_climbing,
    "greedy": _informada(greedy_search.busqueda_voraz),
    "astar": _informada(star_search.busqueda_estrella),
    "dijkstra": lambda g, o, d, h: dijkstra.dijkstra(g, o, d),
}


def comparar(
    grafo: grafos.Grafo,
    origen: str,
    destino: str | None,
    h: dict[str, float] | None,
    algoritmos: list[str],
) -> dict:
    tabla = []
    for clave in algoritmos:
        nombre, clase, complejidad, _, _ = CATALOGO[clave]
        resultado, tiempo_ms, memoria_kb = metricas.medir(
            _FUNCIONES[clave], grafo, origen, destino, h
        )
        resultado.pop("alcance", None)
        tabla.append(
            {
                "clave": clave,
                "algoritmo": nombre,
                "clase": clase,
                "complejidad": complejidad,
                **resultado,
                "tiempo_ms": tiempo_ms,
                "memoria_kb": memoria_kb,
            }
        )

    con_ruta = [fila for fila in tabla if fila["solucion"] and fila["costo"] is not None]
    mejor = min(con_ruta, key=lambda f: (f["costo"], f["tiempo_ms"]), default=None)
    mas_rapido = min(tabla, key=lambda f: f["tiempo_ms"])
    return {
        "tabla": tabla,
        "mejor": mejor["clave"] if mejor else None,
        "mas_rapido": mas_rapido["clave"],
    }
