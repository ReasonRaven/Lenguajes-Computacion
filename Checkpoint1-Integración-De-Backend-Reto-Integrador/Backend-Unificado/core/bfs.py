"""Búsqueda en anchura (BFS, Breadth-First Search).

Búsqueda no informada: no usa pesos ni heurística. Explora el grafo por
niveles con una cola FIFO: primero todos los vecinos del origen (nivel 1),
luego los vecinos de esos (nivel 2), etc.

    cola = [origen]; nivel[origen] = 0
    mientras la cola no esté vacía:
        u = sacar el primero de la cola
        si u es el destino: terminar
        para cada vecino v de u no descubierto:
            nivel[v] = nivel[u] + 1; padre[v] = u; meter v al final de la cola

Con destino devuelve la ruta con el **menor número de aristas** (no
necesariamente la de menor costo). Sin destino calcula el alcance máximo: todos
los nodos alcanzables desde el origen y a cuántos saltos está cada uno.

Cada nodo y cada arista se procesan una vez: O(V + E) en tiempo y O(V) en memoria.
"""

from collections import deque

from core import grafos

ALGORITMO = "Búsqueda en anchura (BFS)"
CLASE = "P"
COMPLEJIDAD = "O(V + E)"


def bfs(grafo: grafos.Grafo, origen: str, destino: str | None = None) -> dict:
    nivel = {origen: 0}
    padres: dict[str, str | None] = {origen: None}
    cola = deque([origen])
    orden_visita: list[str] = []
    aristas_examinadas = 0

    while cola:
        u = cola.popleft()
        orden_visita.append(u)
        if u == destino:
            break
        for v, _ in grafo[u]:
            aristas_examinadas += 1
            if v not in nivel:
                nivel[v] = nivel[u] + 1
                padres[v] = u
                cola.append(v)

    resultado = {
        "nodos_recorridos": len(orden_visita),
        "operaciones": aristas_examinadas,
        "orden_visita": orden_visita,
    }

    if destino is None:
        lejanos = [nodo for nodo, n in nivel.items() if n == max(nivel.values())]
        return {
            **resultado,
            "solucion": True,
            "ruta": [],
            "costo": None,
            "alcance": nivel,
            "motivo": (
                f"Desde {origen} se alcanzan {len(nivel)} de {len(grafo)} nodos. "
                f"Los más lejanos ({', '.join(lejanos)}) están a {max(nivel.values())} "
                "salto(s)."
            ),
        }

    if destino in nivel:
        ruta = grafos.reconstruir_ruta(padres, destino)
        return {
            **resultado,
            "solucion": True,
            "ruta": ruta,
            "costo": grafos.costo_ruta(grafo, ruta),
            "motivo": (
                f"Se llegó a {destino} en {nivel[destino]} salto(s), el mínimo posible; "
                f"el costo de esa ruta es {grafos.costo_ruta(grafo, ruta):g}."
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
