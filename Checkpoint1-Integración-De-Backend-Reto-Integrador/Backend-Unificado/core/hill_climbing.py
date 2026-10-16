"""Ascenso de colinas (Hill-Climbing), en su versión de máxima pendiente.

Búsqueda local con heurística: no guarda frontera ni alternativas, solo el
nodo actual. En cada paso mira a sus vecinos y se mueve al de menor h(n)
(el que "más acerca" al destino), **solo si mejora** a h del nodo actual:

    actual = origen
    mientras actual no sea el destino:
        mejor = vecino no visitado con menor h (desempate: arista más barata)
        si no hay vecino o h(mejor) ≥ h(actual): detenerse (óptimo local)
        actual = mejor

Es muy barato (O(b · d): b vecinos por cada uno de los d pasos, y memoria
O(d) para la ruta), pero es incompleto: se queda atascado en óptimos
locales, mesetas (vecinos con la misma h) o callejones sin salida, aunque
exista un camino al destino. Tampoco garantiza la ruta de menor costo.
"""

import math

from core import grafos

ALGORITMO = "Ascenso de colinas (Hill-Climbing)"
CLASE = "Heurística (búsqueda local)"
COMPLEJIDAD = "O(b · d)"


def hill_climbing(
    grafo: grafos.Grafo, origen: str, destino: str, h: dict[str, float]
) -> dict:
    ruta = [origen]
    en_ruta = {origen}
    vecinos_examinados = 0
    actual = origen
    motivo = ""

    while actual != destino:
        candidatos = [(h[v], w, v) for v, w in grafo[actual] if v not in en_ruta]
        vecinos_examinados += len(grafo[actual])
        if not candidatos:
            motivo = (
                f"Se detuvo en {actual}: no tiene vecinos sin visitar (callejón sin salida)."
            )
            break

        h_mejor, _, mejor = min(candidatos)
        if h_mejor >= h[actual]:
            h_txt = "∞" if math.isinf(h[actual]) else f"{h[actual]:g}"
            motivo = (
                f"Se detuvo en {actual} (h = {h_txt}): ningún vecino mejora la heurística "
                f"(el mejor, {mejor}, tiene h = "
                f"{'∞' if math.isinf(h_mejor) else f'{h_mejor:g}'}). Es un óptimo local "
                "o una meseta."
            )
            break

        ruta.append(mejor)
        en_ruta.add(mejor)
        actual = mejor

    solucion = actual == destino
    if solucion:
        motivo = (
            f"Se llegó a {destino} en {len(ruta) - 1} paso(s), bajando h(n) en cada uno; "
            f"costo {grafos.costo_ruta(grafo, ruta):g}."
        )

    return {
        "solucion": solucion,
        "ruta": ruta if solucion else [],
        "costo": grafos.costo_ruta(grafo, ruta) if solucion else None,
        "nodos_recorridos": len(ruta),
        "operaciones": vecinos_examinados,
        "orden_visita": ruta,
        "motivo": motivo,
    }
