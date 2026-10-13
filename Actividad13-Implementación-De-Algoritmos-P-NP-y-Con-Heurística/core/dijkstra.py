"""Algoritmo de Dijkstra: camino de menor costo entre dos nodos.

Problema en P. Con pesos no negativos, el nodo de la frontera con menor
distancia acumulada ya tiene su distancia definitiva: ningún camino que pase
por otro nodo de la frontera puede salir más barato. Por eso cada nodo se
fija (se "recorre") una sola vez y en orden creciente de distancia.

    dist[origen] = 0
    mientras haya nodos en la frontera:
        u = nodo de la frontera con menor dist
        si u es el destino: terminar
        para cada arista u → v con peso w:
            si dist[u] + w < dist[v]: dist[v] = dist[u] + w   (relajación)

Con cola de prioridad binaria (`heapq`) el costo es O((V + E) log V).
"""

import heapq
import math

from core import grafos

ALGORITMO = "Dijkstra"
CLASE = "P"
COMPLEJIDAD = "O((V + E) log V)"


def dijkstra(grafo: grafos.Grafo, origen: str, destino: str) -> dict:
    distancia = {origen: 0.0}
    padres: dict[str, str | None] = {origen: None}
    fijados: set[str] = set()
    frontera = [(0.0, 0, origen)]  # (distancia, orden de inserción, nodo)
    contador = 0
    relajaciones = 0

    while frontera:
        d_u, _, u = heapq.heappop(frontera)
        if u in fijados:  # entrada obsoleta: ya se fijó con menor distancia
            continue
        fijados.add(u)
        if u == destino:
            break

        for v, w in grafo[u]:
            relajaciones += 1
            d_v = d_u + w
            if d_v < distancia.get(v, math.inf):
                distancia[v] = d_v
                padres[v] = u
                contador += 1
                heapq.heappush(frontera, (d_v, contador, v))

    solucion = destino in fijados
    if solucion:
        motivo = f"Camino de menor costo de {origen} a {destino}: {distancia[destino]:g}."
    else:
        motivo = (
            f"Se recorrieron todos los nodos alcanzables desde {origen} y {destino} "
            "no está entre ellos: no existe camino."
        )

    return {
        "solucion": solucion,
        "ruta": grafos.reconstruir_ruta(padres, destino) if solucion else [],
        "costo": distancia[destino] if solucion else None,
        "nodos_recorridos": len(fijados),
        "operaciones": relajaciones,
        "motivo": motivo,
    }
