"""Algoritmo de Karatsuba (1960), recursivo: divide y vencerás.

Se parte cada número en una mitad alta y una baja de m dígitos:

    x = a · 10^m + b
    y = c · 10^m + d

    x · y = ac · 10^(2m) + (ad + bc) · 10^m + bd

Hacerlo así directamente cuesta 4 productos de la mitad de tamaño
(T(n) = 4T(n/2) + O(n) = O(n²), igual que la escolar). Karatsuba obtiene el
término central con un solo producto extra, reutilizando los otros dos:

    z2 = a · c
    z0 = b · d
    z1 = (a + b)(c + d) − z2 − z0      (= ad + bc)

    x · y = z2 · 10^(2m) + z1 · 10^m + z0

Son 3 productos recursivos más sumas, restas y desplazamientos lineales:

    T(n) = 3T(n/2) + O(n)  →  T(n) = O(n^log₂3) ≈ O(n^1.585)   (Teorema Maestro)

La recursión tiene profundidad ⌈log₂ n⌉ y en cada nivel solo viven las listas
de esa llamada (de tamaño ~n/2^k), así que el espacio extra es
S(n) = O(n + n/2 + n/4 + ...) = O(n).

Variantes:
- **Pura** (`umbral=1`): divide hasta llegar a un dígito por lado.
- **Híbrida** (`umbral>1`): cuando el subproblema tiene `umbral` dígitos o
  menos, lo resuelve con la multiplicación escolar. Para números chicos la
  escolar es más rápida (menos llamadas y listas temporales), así que cortar
  la recursión antes reduce el costo constante sin cambiar la complejidad.
"""

from core.digitos import Digitos, desplazar, quitar_ceros, restar, sumar
from core.tradicional import multiplicar_digitos

ALGORITMO_PURO = "Karatsuba recursivo (puro)"
ALGORITMO_HIBRIDO = "Karatsuba recursivo (híbrido)"
COMPLEJIDAD_TIEMPO = "O(n^log₂3) ≈ O(n^1.585)"
COMPLEJIDAD_ESPACIO = "O(n)"
UMBRAL_HIBRIDO = 16


def karatsuba(x: Digitos, y: Digitos, umbral: int = 1) -> dict:
    """Multiplica `x · y` y reporta el trabajo realizado.

    `multiplicaciones` cuenta los productos de un dígito por un dígito (los
    casos base y, en la híbrida, los de la escolar), comparable con el n·m de
    la tradicional.
    """
    if umbral < 1:
        raise ValueError("umbral debe ser al menos 1")
    contadores = {"multiplicaciones": 0, "llamadas_recursivas": 0, "profundidad": 0}
    digitos = _karatsuba(x, y, umbral, 0, contadores)
    return {"digitos": digitos, **contadores}


def _karatsuba(x: Digitos, y: Digitos, umbral: int, nivel: int, contadores: dict) -> Digitos:
    contadores["llamadas_recursivas"] += 1
    contadores["profundidad"] = max(contadores["profundidad"], nivel)

    n = max(len(x), len(y))
    # Caso base: un dígito por lado (pura) o subproblema chico (híbrida)
    if n <= umbral:
        contadores["multiplicaciones"] += len(x) * len(y)
        return multiplicar_digitos(x, y)

    # Dividir: los m dígitos de abajo y el resto. Con listas little-endian la
    # mitad baja es el prefijo de la lista.
    m = n // 2
    b, a = _partir(x, m)
    d, c = _partir(y, m)

    # Vencer: tres productos recursivos de la mitad de tamaño
    z2 = _karatsuba(a, c, umbral, nivel + 1, contadores)
    z0 = _karatsuba(b, d, umbral, nivel + 1, contadores)
    z1 = _karatsuba(sumar(a, b), sumar(c, d), umbral, nivel + 1, contadores)
    z1 = restar(restar(z1, z2), z0)

    # Combinar: z2 · 10^(2m) + z1 · 10^m + z0
    return quitar_ceros(sumar(sumar(desplazar(z2, 2 * m), desplazar(z1, m)), z0))


def _partir(x: Digitos, m: int) -> tuple[Digitos, Digitos]:
    """Divide x en (baja, alta) tal que x = alta · 10^m + baja."""
    return quitar_ceros(x[:m]), quitar_ceros(x[m:])
