"""Multiplicación tradicional (escolar): la que se hace a mano en papel.

Cada dígito de `x` se multiplica por cada dígito de `y` y el producto parcial
se acumula en la posición `i + j` del resultado, propagando el acarreo:

           1 2 3 4
         × 5 6 7 8
         ---------
           9 8 7 2     ← 1234 · 8
         8 6 3 8       ← 1234 · 7, desplazado una posición
       7 4 0 4         ← 1234 · 6, desplazado dos posiciones
     6 1 7 0           ← 1234 · 5, desplazado tres posiciones
     -------------
     7 0 0 6 6 5 2

Con n y m dígitos hace exactamente n · m multiplicaciones de un dígito:
T(n) = O(n²) para dos números de n dígitos. El espacio extra es el arreglo del
resultado, de n + m posiciones: S(n) = O(n).
"""

from core.digitos import Digitos, quitar_ceros

ALGORITMO = "Multiplicación tradicional (escolar)"
COMPLEJIDAD_TIEMPO = "O(n²)"
COMPLEJIDAD_ESPACIO = "O(n)"


def multiplicar_digitos(x: Digitos, y: Digitos) -> Digitos:
    """Producto escolar de dos listas de dígitos little-endian."""
    resultado = [0] * (len(x) + len(y))
    for i, dx in enumerate(x):
        acarreo = 0
        for j, dy in enumerate(y):
            t = resultado[i + j] + dx * dy + acarreo
            resultado[i + j] = t % 10
            acarreo = t // 10
        resultado[i + len(y)] += acarreo
    return quitar_ceros(resultado)


def tradicional(x: Digitos, y: Digitos) -> dict:
    """Multiplica `x · y` y reporta el trabajo realizado."""
    return {
        "digitos": multiplicar_digitos(x, y),
        "multiplicaciones": len(x) * len(y),
        "llamadas_recursivas": 0,
        "profundidad": 0,
    }
