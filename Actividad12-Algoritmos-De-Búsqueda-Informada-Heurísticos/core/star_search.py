"""Búsqueda A* (A estrella).

Función de evaluación:

    f(n) = g(n) + h(n)

- g(n): costo acumulado desde el origen, la suma de los pesos conocidos.
- h(n): estimación del costo que falta para llegar al destino.

Se expande siempre el nodo de la frontera con menor f(n); a igual f se
prefiere el de menor g y después el orden de inserción. Cuando se encuentra un
camino más barato hacia un nodo ya generado se actualiza su g y su padre y se
vuelve a insertar (la entrada vieja de la cola se descarta al salir). Si el
nodo ya se había expandido se reabre, lo que mantiene la ruta óptima incluso
con heurísticas admisibles que no son consistentes. Con h admisible, A*
devuelve la ruta de menor costo.
"""

import heapq
import math
import time

from core import grafos

ALGORITMO = "Búsqueda A*"
CRITERIO = "f(n) = g(n) + h(n)"


def busqueda_estrella(
    grafo: grafos.Grafo,
    origen: str,
    destino: str,
    h: dict[str, float],
    limite: int,
) -> dict:
    inicio = time.perf_counter()

    contador = 0
    frontera = [(h[origen], 0.0, contador, origen)]  # (f, g, orden de inserción, nodo)
    en_frontera = {origen}
    mejor_g = {origen: 0.0}
    padres: dict[str, str | None] = {origen: None}
    profundidad = {origen: 0}
    cerrados: set[str] = set()
    traza: list[dict] = []
    max_frontera = max_memoria = 1

    solucion = False
    motivo = (
        f"Se exploraron todos los nodos alcanzables desde {origen} y {destino} "
        "no está entre ellos: no existe camino."
    )
    costo = None

    while frontera:
        f_u, g_u, _, u = heapq.heappop(frontera)
        if g_u > mejor_g[u] or u in cerrados:  # entrada obsoleta
            continue
        en_frontera.discard(u)
        cerrados.add(u)
        traza.append({"nodo": u, "g": g_u, "h": grafos.numero(h[u]), "f": grafos.numero(f_u)})

        if u == destino:
            solucion, costo = True, g_u
            motivo = f"Se llegó a {destino} con costo {g_u:g}."
            break
        if len(traza) >= limite:
            motivo = f"Se alcanzó el límite de {limite} nodos visitados sin llegar a {destino}."
            break

        for v, w in grafo[u]:
            g_v = g_u + w
            if g_v < mejor_g.get(v, math.inf):
                mejor_g[v] = g_v
                padres[v] = u
                profundidad[v] = profundidad[u] + 1
                cerrados.discard(v)  # reapertura (solo con h inconsistente)
                contador += 1
                heapq.heappush(frontera, (g_v + h[v], g_v, contador, v))
                en_frontera.add(v)

        max_frontera = max(max_frontera, len(en_frontera))
        max_memoria = max(max_memoria, len(en_frontera) + len(cerrados))

    tiempo_ms = (time.perf_counter() - inicio) * 1000

    # d: profundidad de la solución o, si no la hay, la mayor profundidad alcanzada
    d = profundidad[destino] if solucion else max(profundidad.values())

    return {
        "algoritmo": ALGORITMO,
        "criterio": CRITERIO,
        "nodos_visitados": len(traza),
        "solucion": solucion,
        "ruta": grafos.reconstruir_ruta(padres, destino) if solucion else [],
        "costo": costo,
        "motivo": motivo,
        **grafos.complejidades(
            notacion="O(b^d)",
            b=grafos.factor_ramificacion(grafo, origen),
            profundidad=d,
            nodos_generados=contador + 1,
            tiempo_ms=tiempo_ms,
            max_frontera=max_frontera,
            max_memoria=max_memoria,
        ),
        "traza": traza,
    }
