"""Problema del agente viajero (TSP): ciclo de menor costo que sale del
origen, pasa exactamente una vez por cada nodo y regresa al origen.

Es NP-difícil: no se conoce un algoritmo de tiempo polinomial que lo resuelva
de forma exacta. Aquí hay dos versiones:

- `tsp_exacto`: programación dinámica de Held-Karp. Garantiza el óptimo,
  pero su tiempo y memoria crecen exponencialmente con el número de nodos.
- `tsp_voraz`: heurística del vecino más cercano. Polinomial, pero no
  garantiza el óptimo y en grafos incompletos puede quedarse sin salida.

Si el grafo no es completo, las aristas que faltan cuentan como costo ∞.
"""

import math

from core import grafos

# Held-Karp con 18 nodos tarda ~1.5 s y reserva ~55 MB; cada nodo extra
# duplica (de sobra) ambos.
MAX_NODOS_EXACTO = 18

EXACTO = {
    "algoritmo": "TSP exacto (programación dinámica de Held-Karp)",
    "clase": "NP-difícil",
    "complejidad": "O(n² · 2ⁿ) tiempo, O(n · 2ⁿ) memoria",
}
VORAZ = {
    "algoritmo": "TSP con heurística voraz (vecino más cercano)",
    "clase": "Heurística (aproximación polinomial)",
    "complejidad": "O(n²)",
}


def _matriz_pesos(grafo: grafos.Grafo, nodos: list[str]) -> list[list[float]]:
    indice = {nodo: i for i, nodo in enumerate(nodos)}
    pesos = [[math.inf] * len(nodos) for _ in nodos]
    for u, vecinos in grafo.items():
        for v, w in vecinos:
            pesos[indice[u]][indice[v]] = w
    return pesos


def _sin_ciclo(motivo: str, nodos_recorridos: int, operaciones: int) -> dict:
    return {
        "solucion": False,
        "ruta": [],
        "costo": None,
        "nodos_recorridos": nodos_recorridos,
        "operaciones": operaciones,
        "motivo": motivo,
    }


def tsp_exacto(grafo: grafos.Grafo, origen: str) -> dict:
    """Held-Karp. Se numeran los nodos con el origen en 0 y el resto de 1 a
    n − 1. Un estado (S, j) es "el camino más barato que sale del origen,
    visita exactamente los nodos del conjunto S y termina en j ∈ S":

        C({j}, j)     = w(origen, j)
        C(S ∪ {k}, k) = min sobre j ∈ S de C(S, j) + w(j, k)
        óptimo        = min sobre j de C(todos, j) + w(j, origen)

    S se guarda como máscara de bits (el bit j − 1 indica si j ∈ S). Como
    S ∪ {k} siempre es un número mayor que S, basta recorrer las máscaras en
    orden creciente.

    Los nodos recorridos son los estados (S, j) alcanzables que se
    expandieron; las operaciones, las transiciones C(S, j) + w(j, k)
    evaluadas.
    """
    nodos = [origen] + [nodo for nodo in grafo if nodo != origen]
    n = len(nodos)
    if n == 1:
        return {
            "solucion": True,
            "ruta": [origen],
            "costo": 0.0,
            "nodos_recorridos": 1,
            "operaciones": 0,
            "motivo": "El grafo tiene un solo nodo: el ciclo es trivial.",
        }

    pesos = _matriz_pesos(grafo, nodos)
    m = n - 1  # nodos distintos del origen; el nodo i + 1 usa el bit i
    completo = (1 << m) - 1
    costo = [[math.inf] * m for _ in range(1 << m)]
    previo = [[-1] * m for _ in range(1 << m)]
    for j in range(m):
        costo[1 << j][j] = pesos[0][j + 1]

    estados = transiciones = 0
    for mascara in range(1, 1 << m):
        fila = costo[mascara]
        for j in range(m):
            c = fila[j]
            if c == math.inf:  # j ∉ S o no hay camino que termine en j
                continue
            estados += 1
            pesos_j = pesos[j + 1]
            for k in range(m):
                if mascara & (1 << k) or pesos_j[k + 1] == math.inf:
                    continue
                transiciones += 1
                siguiente = mascara | (1 << k)
                nuevo = c + pesos_j[k + 1]
                if nuevo < costo[siguiente][k]:
                    costo[siguiente][k] = nuevo
                    previo[siguiente][k] = j

    mejor, ultimo = min(
        (costo[completo][j] + pesos[j + 1][0], j) for j in range(m)
    )
    if mejor == math.inf:
        return _sin_ciclo(
            "No existe un ciclo que pase por todos los nodos (ciclo hamiltoniano): "
            "al grafo le faltan aristas.",
            estados,
            transiciones,
        )

    camino = []  # del último nodo al primero, siguiendo `previo`
    mascara, j = completo, ultimo
    while j != -1:
        camino.append(nodos[j + 1])
        mascara, j = mascara & ~(1 << j), previo[mascara][j]
    ruta = [origen, *camino[::-1], origen]

    return {
        "solucion": True,
        "ruta": ruta,
        "costo": mejor,
        "nodos_recorridos": estados,
        "operaciones": transiciones,
        "motivo": f"Ciclo óptimo de costo {mejor:g} ({estados} estados evaluados).",
    }


def tsp_voraz(grafo: grafos.Grafo, origen: str) -> dict:
    """Vecino más cercano: desde el nodo actual se avanza siempre por la
    arista más barata hacia un nodo no visitado (a igual peso, el primero en
    la lista de adyacencia). Al visitar todos se regresa al origen.

    Nunca se deshace una decisión, por eso es rápido; pero una elección
    barata al principio puede obligar a aristas caras al final, o dejar al
    agente en un nodo sin vecinos libres (o sin arista de regreso) aunque sí
    exista un ciclo.

    Los nodos recorridos son los visitados por el agente; las operaciones,
    las aristas examinadas al elegir cada paso.
    """
    n = len(grafo)
    ruta = [origen]
    visitados = {origen}
    costo = 0.0
    examinadas = 0
    actual = origen

    while len(ruta) < n:
        mejor: tuple[float, str] | None = None
        for v, w in grafo[actual]:
            examinadas += 1
            if v not in visitados and (mejor is None or w < mejor[0]):
                mejor = (w, v)
        if mejor is None:
            return _sin_ciclo(
                f"El agente quedó en {actual} sin vecinos por visitar tras recorrer "
                f"{len(ruta)} de {n} nodos ({' → '.join(ruta)}).",
                len(ruta),
                examinadas,
            )
        w, actual = mejor
        ruta.append(actual)
        visitados.add(actual)
        costo += w

    regreso = None
    for v, w in grafo[actual]:
        examinadas += 1
        if v == origen:
            regreso = w
    if regreso is None and n > 1:
        return _sin_ciclo(
            f"Se visitaron los {n} nodos, pero no hay arista de {actual} de regreso a "
            f"{origen} para cerrar el ciclo.",
            len(ruta),
            examinadas,
        )
    if n > 1:
        ruta.append(origen)
        costo += regreso

    return {
        "solucion": True,
        "ruta": ruta,
        "costo": costo,
        "nodos_recorridos": len(visitados),
        "operaciones": examinadas,
        "motivo": f"Ciclo encontrado con costo {costo:g} (no necesariamente óptimo).",
    }
