"""Construcción de grafos ponderados y utilidades compartidas por la búsqueda
voraz y la búsqueda A*.

Internamente un grafo es una lista de adyacencia: un diccionario
nodo -> lista de (vecino, peso), con una fila (posiblemente vacía) para cada
nodo. Es el mismo formato del archivo de la actividad, con tuplas en lugar de
listas de dos elementos.
"""

import math
from collections import deque

Grafo = dict[str, list[tuple[str, float]]]

PORCENTAJE_LIMITE = 0.8


class GrafoInvalido(ValueError):
    """La entrada no describe un grafo ponderado bien formado."""


# ---------------------------------------------------------------------------
# Construcción y validación
# ---------------------------------------------------------------------------


def construir_grafo(
    lista: dict[str, list[tuple[str, float]]] | None = None,
    matriz: list[list[float | None]] | None = None,
    nodos: list[str] | None = None,
    aristas: list[tuple[str, str, float]] | None = None,
    dirigido: bool = True,
) -> Grafo:
    """Normaliza cualquiera de los tres formatos de entrada a lista de
    adyacencia. Exactamente uno de `lista`, `matriz` o `aristas` debe venir."""
    enviados = [f for f in (lista, matriz, aristas) if f is not None]
    if len(enviados) != 1:
        raise GrafoInvalido(
            "Envía exactamente un formato de grafo: lista_adyacencia, "
            "matriz_adyacencia (con nodos) o aristas."
        )

    if lista is not None:
        declarados = list(lista)
        tripletas = [(u, v, w) for u, vecinos in lista.items() for v, w in vecinos]
    elif matriz is not None:
        declarados = list(nodos or [])
        tripletas = _aristas_de_matriz(matriz, nodos)
    else:
        declarados = []
        tripletas = list(aristas)

    grafo: Grafo = {nodo: [] for nodo in declarados}
    for u, v, w in tripletas:
        if w < 0:
            raise GrafoInvalido(
                f"La arista {u} → {v} tiene peso negativo ({w:g}); "
                "la búsqueda informada requiere pesos ≥ 0."
            )
        grafo.setdefault(u, [])
        grafo.setdefault(v, [])  # nodos que solo aparecen como destino (p. ej. J)
        _agregar_arista(grafo, u, v, w)
        if not dirigido:
            _agregar_arista(grafo, v, u, w)

    if not grafo:
        raise GrafoInvalido("El grafo está vacío.")
    return grafo


def _aristas_de_matriz(
    matriz: list[list[float | None]], nodos: list[str] | None
) -> list[tuple[str, str, float]]:
    """Una celda con 0 o null significa que no hay arista."""
    if not nodos:
        raise GrafoInvalido(
            "La matriz de adyacencia requiere `nodos`: el nombre de cada fila/columna."
        )
    n = len(nodos)
    if len(set(nodos)) != n:
        raise GrafoInvalido("La lista `nodos` tiene nombres repetidos.")
    if len(matriz) != n or any(len(fila) != n for fila in matriz):
        raise GrafoInvalido(
            f"La matriz debe ser cuadrada de {n}×{n}: una fila y una columna por nodo."
        )
    return [
        (nodos[i], nodos[j], peso)
        for i, fila in enumerate(matriz)
        for j, peso in enumerate(fila)
        if peso
    ]


def _agregar_arista(grafo: Grafo, u: str, v: str, w: float) -> None:
    """Si la arista ya existe se conserva el peso menor."""
    for i, (vecino, peso) in enumerate(grafo[u]):
        if vecino == v:
            if w < peso:
                grafo[u][i] = (v, w)
            return
    grafo[u].append((v, w))


def validar_coordenadas(grafo: Grafo, coordenadas: dict | None) -> None:
    if not coordenadas:
        raise GrafoInvalido(
            "La heurística euclidiana requiere `coordenadas`: una posición [x, y] por nodo."
        )
    faltantes = [nodo for nodo in grafo if nodo not in coordenadas]
    if faltantes:
        raise GrafoInvalido("Faltan coordenadas para: " + ", ".join(faltantes))


def limite_por_defecto(total_nodos: int) -> int:
    """80 % del número total de nodos, redondeado hacia arriba."""
    return max(1, math.ceil(PORCENTAJE_LIMITE * total_nodos))


# ---------------------------------------------------------------------------
# Heurísticas
# ---------------------------------------------------------------------------


def heuristica_euclidiana(
    grafo: Grafo, coordenadas: dict[str, tuple[float, float]], destino: str
) -> tuple[dict[str, float], float]:
    """h(n) = k · d(n, destino), con d la distancia euclidiana.

    Las coordenadas no están en las mismas unidades que los pesos, así que se
    escalan con k = min(w(u, v) / d(u, v)) sobre todas las aristas. Así
    k·d(u, v) ≤ w(u, v) para toda arista y, por la desigualdad del triángulo,
    h(u) ≤ k·d(u, v) + h(v) ≤ w(u, v) + h(v): la heurística es consistente y
    por lo tanto admisible. Las aristas entre nodos con la misma posición no
    entran en el mínimo (para ellas h(u) = h(v) y la desigualdad se cumple).
    """
    validar_coordenadas(grafo, coordenadas)
    razones = [
        w / d
        for u, vecinos in grafo.items()
        for v, w in vecinos
        if (d := math.dist(coordenadas[u], coordenadas[v])) > 0
    ]
    k = min(razones, default=0.0)
    meta = coordenadas[destino]
    return {nodo: k * math.dist(coordenadas[nodo], meta) for nodo in grafo}, k


def heuristica_saltos(grafo: Grafo, destino: str) -> tuple[dict[str, float], float]:
    """h(n) = w_min · saltos(n, destino), donde saltos es el mínimo número de
    aristas para llegar al destino (BFS sobre el grafo invertido) y w_min el
    peso más pequeño del grafo.

    Cada salto cuesta al menos w_min, así que nunca sobreestima; y como
    saltos(u) ≤ 1 + saltos(v), h(u) ≤ w_min + h(v) ≤ w(u, v) + h(v):
    también es consistente. Los nodos desde los que no se puede llegar al
    destino reciben h = ∞.
    """
    inverso: dict[str, list[str]] = {nodo: [] for nodo in grafo}
    for u, vecinos in grafo.items():
        for v, _ in vecinos:
            inverso[v].append(u)

    saltos = {destino: 0}
    cola = deque([destino])
    while cola:
        actual = cola.popleft()
        for previo in inverso[actual]:
            if previo not in saltos:
                saltos[previo] = saltos[actual] + 1
                cola.append(previo)

    w_min = min((w for vecinos in grafo.values() for _, w in vecinos), default=0.0)
    return {
        nodo: w_min * saltos[nodo] if nodo in saltos else math.inf for nodo in grafo
    }, w_min


# ---------------------------------------------------------------------------
# Utilidades de los algoritmos
# ---------------------------------------------------------------------------


def reconstruir_ruta(padres: dict[str, str | None], destino: str) -> list[str]:
    ruta = []
    nodo: str | None = destino
    while nodo is not None:
        ruta.append(nodo)
        nodo = padres[nodo]
    return ruta[::-1]


def alcanzables(grafo: Grafo, origen: str) -> list[str]:
    vistos = {origen}
    pila = [origen]
    while pila:
        for v, _ in grafo[pila.pop()]:
            if v not in vistos:
                vistos.add(v)
                pila.append(v)
    return [nodo for nodo in grafo if nodo in vistos]


def factor_ramificacion(grafo: Grafo, origen: str) -> int:
    """b: el mayor número de sucesores entre los nodos alcanzables."""
    return max(len(grafo[nodo]) for nodo in alcanzables(grafo, origen))


def profundidad_maxima(grafo: Grafo, origen: str) -> int:
    """m: la mayor profundidad del espacio de búsqueda desde el origen.

    En un grafo acíclico es el camino más largo (en aristas), calculado con un
    orden topológico. Si hay ciclos se acota con alcanzables − 1, el camino
    simple más largo posible.
    """
    nodos = alcanzables(grafo, origen)
    entrantes = {nodo: 0 for nodo in nodos}
    for u in nodos:
        for v, _ in grafo[u]:
            entrantes[v] += 1

    cola = deque(nodo for nodo in nodos if entrantes[nodo] == 0)
    orden = []
    while cola:
        u = cola.popleft()
        orden.append(u)
        for v, _ in grafo[u]:
            entrantes[v] -= 1
            if entrantes[v] == 0:
                cola.append(v)

    if len(orden) < len(nodos):
        return len(nodos) - 1

    profundidad = {origen: 0}
    for u in orden:
        for v, _ in grafo[u]:
            profundidad[v] = max(profundidad.get(v, 0), profundidad[u] + 1)
    return max(profundidad.values())


def numero(valor: float) -> float | None:
    """Redondea para la salida JSON; ∞ no existe en JSON y se reporta como null."""
    return None if math.isinf(valor) else round(valor, 4)


def complejidades(
    notacion: str,
    b: int,
    profundidad: int,
    nodos_generados: int,
    tiempo_ms: float,
    max_frontera: int,
    max_memoria: int,
) -> dict:
    """Arma T(n) y S(n): la cota teórica b^profundidad y lo medido en la ejecución."""
    teorica = {"notacion": notacion, "b": b, "profundidad": profundidad, "cota": b**profundidad}
    return {
        "T(n)": {**teorica, "nodos_generados": nodos_generados, "tiempo_ms": round(tiempo_ms, 4)},
        "S(n)": {**teorica, "max_frontera": max_frontera, "max_nodos_en_memoria": max_memoria},
    }
