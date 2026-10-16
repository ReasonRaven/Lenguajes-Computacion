"""Generador de grafos sintéticos ponderados (y de listas para el benchmark).

1. Se crean n nodos con nombres A, B, ..., Z, AA, AB, ... y una posición
   aleatoria (x, y) en el cuadrado [0, 100] × [0, 100].
2. Se baraja el orden de los nodos y se unen en un ciclo
   (n₁ → n₂ → ... → nₙ → n₁). Así el grafo siempre es (fuertemente) conexo y
   siempre tiene al menos un ciclo hamiltoniano: Dijkstra encuentra camino
   entre cualquier par y el TSP exacto siempre tiene solución.
3. Cada uno de los demás pares de nodos recibe una arista con probabilidad
   `densidad` (1 = grafo completo).
4. El peso de cada arista es un entero aleatorio en [peso_min, peso_max], o la
   distancia euclidiana redondeada entre sus extremos (`pesos="euclidianos"`).

Con la misma `semilla` se obtiene siempre el mismo grafo.
"""

import math
import random
import string
from itertools import combinations, permutations
from typing import Literal


def nombre_nodo(i: int) -> str:
    """0 → A, 25 → Z, 26 → AA, 27 → AB, ... (como columnas de hoja de cálculo)."""
    nombre = ""
    i += 1
    while i:
        i, resto = divmod(i - 1, 26)
        nombre = string.ascii_uppercase[resto] + nombre
    return nombre


def generar_grafo(
    n: int,
    densidad: float = 0.5,
    peso_min: int = 1,
    peso_max: int = 100,
    pesos: Literal["aleatorios", "euclidianos"] = "aleatorios",
    dirigido: bool = False,
    semilla: int | None = None,
) -> dict:
    rng = random.Random(semilla)
    nodos = [nombre_nodo(i) for i in range(n)]
    coordenadas = {nodo: (rng.randint(0, 100), rng.randint(0, 100)) for nodo in nodos}

    def peso(u: str, v: str) -> int:
        if pesos == "euclidianos":
            return max(1, round(math.dist(coordenadas[u], coordenadas[v])))
        return rng.randint(peso_min, peso_max)

    def clave(u: str, v: str) -> tuple[str, str]:
        # sin dirección, {u, v} se guarda una sola vez, en el orden de `nodos`
        return (u, v) if dirigido or nodos.index(u) < nodos.index(v) else (v, u)

    orden = nodos[:]
    rng.shuffle(orden)
    pares = {clave(orden[i], orden[(i + 1) % n]) for i in range(n) if n > 1}

    todos = permutations(nodos, 2) if dirigido else combinations(nodos, 2)
    for par in todos:
        if par not in pares and rng.random() < densidad:
            pares.add(par)

    lista: dict[str, list[list]] = {nodo: [] for nodo in nodos}
    for u, v in sorted(pares, key=lambda p: (nodos.index(p[0]), nodos.index(p[1]))):
        lista[u].append([v, peso(u, v)])

    posibles = n * (n - 1) if dirigido else n * (n - 1) // 2
    return {
        "n": n,
        "num_aristas": len(pares),
        "densidad_real": round(len(pares) / posibles, 4) if posibles else 0.0,
        "dirigido": dirigido,
        "semilla": semilla,
        "lista_adyacencia": lista,
        "coordenadas": coordenadas,
    }


# ---------------------------------------------------------------------------
# Listas para el benchmark de ordenamiento
# ---------------------------------------------------------------------------

Distribucion = Literal["aleatoria", "ordenada", "inversa", "casi_ordenada"]


def generar_lista(
    n: int, distribucion: Distribucion = "aleatoria", semilla: int | None = None
) -> list[int]:
    """n enteros en [0, 10·n] (al menos [0, 100]).

    - `aleatoria`: orden aleatorio (caso promedio).
    - `ordenada`: ya ordenada (mejor caso de burbuja e inserción).
    - `inversa`: de mayor a menor (peor caso de burbuja e inserción).
    - `casi_ordenada`: ordenada con ~5 % de pares intercambiados al azar.
    """
    rng = random.Random(semilla)
    datos = [rng.randint(0, max(100, 10 * n)) for _ in range(n)]
    if distribucion == "ordenada":
        datos.sort()
    elif distribucion == "inversa":
        datos.sort(reverse=True)
    elif distribucion == "casi_ordenada":
        datos.sort()
        for _ in range(max(1, n // 20) if n > 1 else 0):
            i, j = rng.randrange(n), rng.randrange(n)
            datos[i], datos[j] = datos[j], datos[i]
    return datos
