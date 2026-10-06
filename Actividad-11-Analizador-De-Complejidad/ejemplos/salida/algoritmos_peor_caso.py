def raizCuadrada(n):                                             # Complejidad de raizCuadrada: O(log n)
    if n < 0:                                                    # O(1)
        return None                                              # O(1)
    x = n                                                        # O(1)
    y = (x + 1) // 2                                             # O(1)
    while y < x:                                                 # O(log n)
        x = y                                                    # O(log n)
        y = (x + n // x) // 2                                    # O(log n)
    return x                                                     # O(1)


def factorial(n):                                                # Complejidad de factorial: O(n)
    if n < 0:                                                    # O(1)
        return None                                              # O(1)
    resultado = 1                                                # O(1)
    for i in range(2, n + 1):                                    # O(n)
        resultado *= i                                           # O(n)
    return resultado                                             # O(1)


def burbuja(lista):                                              # Complejidad de burbuja: O(n²)
    n = len(lista)                                               # O(1)
    for i in range(n):                                           # O(n)
        for j in range(0, n - i - 1):                            # O(n²)
            if lista[j] > lista[j + 1]:                          # O(n²)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # O(n²)
    return lista                                                 # O(1)


def ordenacionBinaria(lista, objetivo):                          # Complejidad de ordenacionBinaria: O(log n)
    izquierda, derecha = 0, len(lista) - 1                       # O(1)
    while izquierda <= derecha:                                  # O(log n)
        medio = (izquierda + derecha) // 2                       # O(log n)
        if lista[medio] == objetivo:                             # O(log n)
            return medio                                         # O(log n)
        elif lista[medio] < objetivo:                            # O(log n)
            izquierda = medio + 1                                # O(log n)
        else:
            derecha = medio - 1                                  # O(log n)
    return -1                                                    # O(1)


# ==============================================================================
# RESUMEN DE COMPLEJIDAD — PEOR CASO (notación Big-O)
# Archivo analizado: algoritmos.py
# ==============================================================================
#
# raizCuadrada (línea 1)
#   Suma de complejidades : O(1) + O(1) + O(1) + O(1) + O(log n) + O(log n) + O(log n)
#                           + O(1)
#   Términos agrupados    : 5·O(1) + 3·O(log n)
#   Mayor grado           : O(log n)
#
# factorial (línea 12)
#   Suma de complejidades : O(1) + O(1) + O(1) + O(n) + O(n) + O(1)
#   Términos agrupados    : 4·O(1) + 2·O(n)
#   Mayor grado           : O(n)
#
# burbuja (línea 21)
#   Suma de complejidades : O(1) + O(n) + O(n²) + O(n²) + O(n²) + O(1)
#   Términos agrupados    : 2·O(1) + 1·O(n) + 3·O(n²)
#   Mayor grado           : O(n²)
#
# ordenacionBinaria (línea 30)
#   Suma de complejidades : O(1) + O(log n) + O(log n) + O(log n) + O(log n) + O(log n)
#                           + O(log n) + O(log n) + O(1)
#   Términos agrupados    : 2·O(1) + 7·O(log n)
#   Mayor grado           : O(log n)
#
# ------------------------------------------------------------------------------
# PROGRAMA COMPLETO
#   Suma de complejidades : O(log n) + O(n) + O(n²) + O(log n)
#   Términos agrupados    : 13·O(1) + 10·O(log n) + 3·O(n) + 3·O(n²)
#   Mayor grado           : O(n²)  →  burbuja
# ==============================================================================
