"""Búsqueda en profundidad (DFS, Depth-First Search).

Búsqueda no informada: no usa pesos ni heurística. Con una pila LIFO avanza
siempre por el primer vecino no visitado hasta que ya no puede seguir, y
entonces retrocede (backtracking) al último nodo con vecinos pendientes.

    pila = [origen]
    mientras la pila no esté vacía:
        u = sacar el tope de la pila
        si u ya fue visitado: continuar
        marcar u; si u es el destino: terminar
        meter a la pila los vecinos no visitados (en orden inverso, para
        visitarlos en el orden de la lista de adyacencia)

Encuentra *una* ruta, no la más corta ni la de menor costo: depende del
orden de los vecinos. Sin destino recorre todo lo alcanzable y reporta la
profundidad de cada nodo en el árbol DFS.

O(V + E) en tiempo y O(V) en memoria.
"""

from core import grafos

ALGORITMO = "Búsqueda en profundidad (DFS)"
CLASE = "P"
COMPLEJIDAD = "O(V + E)"


def dfs(grafo: grafos.Grafo, origen: str, destino: str | None = None) -> dict:
    profundidad: dict[str, int] = {}
    padres: dict[str, str | None] = {}
    pila: list[tuple[str, str | None, int]] = [(origen, None, 0)]  # (nodo, padre, profundidad)
    orden_visita: list[str] = []
    aristas_examinadas = 0

    while pila:
        u, padre, p = pila.pop()
        if u in profundidad:
            continue
        profundidad[u] = p
        padres[u] = padre
        orden_visita.append(u)
        if u == destino:
            break
        for v, _ in reversed(grafo[u]):
            aristas_examinadas += 1
            if v not in profundidad:
                pila.append((v, u, p + 1))

    resultado = {
        "nodos_recorridos": len(orden_visita),
        "operaciones": aristas_examinadas,
        "orden_visita": orden_visita,
    }

    if destino is None:
        return {
            **resultado,
            "solucion": True,
            "ruta": [],
            "costo": None,
            "alcance": profundidad,
            "motivo": (
                f"Desde {origen} se alcanzan {len(profundidad)} de {len(grafo)} nodos. "
                f"La rama más profunda del árbol DFS llega a {max(profundidad.values())} "
                "nivel(es)."
            ),
        }

    if destino in profundidad:
        ruta = grafos.reconstruir_ruta(padres, destino)
        return {
            **resultado,
            "solucion": True,
            "ruta": ruta,
            "costo": grafos.costo_ruta(grafo, ruta),
            "motivo": (
                f"Se llegó a {destino} siguiendo la primera rama que lo alcanza "
                f"({len(ruta) - 1} salto(s), costo {grafos.costo_ruta(grafo, ruta):g}); "
                "no tiene por qué ser la ruta más corta ni la más barata."
            ),
        }

    return {
        **resultado,
        "solucion": False,
        "ruta": [],
        "costo": None,
        "motivo": (
            f"Se recorrieron todos los nodos alcanzables desde {origen} y {destino} "
            "no está entre ellos: no existe camino."
        ),
    }
