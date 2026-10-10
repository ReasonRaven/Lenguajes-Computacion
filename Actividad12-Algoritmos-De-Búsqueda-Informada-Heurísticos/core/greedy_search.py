"""Búsqueda voraz (Greedy Best-First Search).

Criterio de selección: de todos los nodos en la frontera se expande el de
menor h(n), es decir, el que la heurística estima más cercano al destino:

    f(n) = h(n)

El costo acumulado g(n) no interviene en la decisión; solo se usa para
desempatar (a igual h se prefiere el nodo alcanzado con menor costo) y,
después, el orden de inserción en la frontera.

Es búsqueda en grafo: un nodo ya generado no se vuelve a meter a la frontera,
aunque después aparezca un camino más barato hacia él. Por eso es rápida pero
no garantiza la ruta óptima.
"""

import heapq
import time

from core import grafos

ALGORITMO = "Búsqueda voraz (Greedy Best-First)"
CRITERIO = "f(n) = h(n)"


def busqueda_voraz(
    grafo: grafos.Grafo,
    origen: str,
    destino: str,
    h: dict[str, float],
    limite: int,
) -> dict:
    inicio = time.perf_counter()

    contador = 0
    frontera = [(h[origen], 0.0, contador, origen)]  # (h, g, orden de inserción, nodo)
    en_frontera = {origen}
    padres: dict[str, str | None] = {origen: None}
    explorados: set[str] = set()
    traza: list[dict] = []
    max_frontera = max_memoria = 1

    solucion = False
    motivo = (
        f"Se exploraron todos los nodos alcanzables desde {origen} y {destino} "
        "no está entre ellos: no existe camino."
    )
    costo = None

    while frontera:
        h_u, g_u, _, u = heapq.heappop(frontera)
        en_frontera.discard(u)
        explorados.add(u)
        traza.append({"nodo": u, "g": g_u, "h": grafos.numero(h_u), "f": grafos.numero(h_u)})

        if u == destino:
            solucion, costo = True, g_u
            motivo = f"Se llegó a {destino} con costo {g_u:g}."
            break
        if len(explorados) >= limite:
            motivo = f"Se alcanzó el límite de {limite} nodos visitados sin llegar a {destino}."
            break

        for v, w in grafo[u]:
            if v in padres:  # ya generado: está en la frontera o ya se expandió
                continue
            padres[v] = u
            contador += 1
            heapq.heappush(frontera, (h[v], g_u + w, contador, v))
            en_frontera.add(v)

        max_frontera = max(max_frontera, len(en_frontera))
        max_memoria = max(max_memoria, len(en_frontera) + len(explorados))

    tiempo_ms = (time.perf_counter() - inicio) * 1000

    return {
        "algoritmo": ALGORITMO,
        "criterio": CRITERIO,
        "nodos_visitados": len(traza),
        "solucion": solucion,
        "ruta": grafos.reconstruir_ruta(padres, destino) if solucion else [],
        "costo": costo,
        "motivo": motivo,
        **grafos.complejidades(
            notacion="O(b^m)",
            b=grafos.factor_ramificacion(grafo, origen),
            profundidad=grafos.profundidad_maxima(grafo, origen),
            nodos_generados=contador + 1,
            tiempo_ms=tiempo_ms,
            max_frontera=max_frontera,
            max_memoria=max_memoria,
        ),
        "traza": traza,
    }
