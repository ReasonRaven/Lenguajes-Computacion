def raizCuadrada(n):                                             # Complejidad de raizCuadrada: Ω(log n)
    if n < 0:                                                    # Ω(1)  ← validación / caso base: no cuenta en el mejor caso
        return None                                              # Ω(1)  ← validación / caso base: no cuenta en el mejor caso
    x = n                                                        # Ω(1)
    y = (x + 1) // 2                                             # Ω(1)
    while y < x:                                                 # Ω(log n)
        x = y                                                    # Ω(log n)
        y = (x + n // x) // 2                                    # Ω(log n)
    return x                                                     # Ω(1)


def factorial(n):                                                # Complejidad de factorial: Ω(n)
    if n < 0:                                                    # Ω(1)  ← validación / caso base: no cuenta en el mejor caso
        return None                                              # Ω(1)  ← validación / caso base: no cuenta en el mejor caso
    resultado = 1                                                # Ω(1)
    for i in range(2, n + 1):                                    # Ω(n)
        resultado *= i                                           # Ω(n)
    return resultado                                             # Ω(1)


def burbuja(lista):                                              # Complejidad de burbuja: Ω(n²)
    n = len(lista)                                               # Ω(1)
    for i in range(n):                                           # Ω(n)
        for j in range(0, n - i - 1):                            # Ω(n²)
            if lista[j] > lista[j + 1]:                          # Ω(n²)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # Ω(n²)
    return lista                                                 # Ω(1)


def ordenacionBinaria(lista, objetivo):                          # Complejidad de ordenacionBinaria: Ω(1)
    izquierda, derecha = 0, len(lista) - 1                       # Ω(1)
    while izquierda <= derecha:                                  # Ω(1)  ← puede terminar en la primera iteración (return/break)
        medio = (izquierda + derecha) // 2                       # Ω(1)
        if lista[medio] == objetivo:                             # Ω(1)
            return medio                                         # Ω(1)
        elif lista[medio] < objetivo:                            # Ω(1)
            izquierda = medio + 1                                # Ω(1)
        else:
            derecha = medio - 1                                  # Ω(1)
    return -1                                                    # Ω(1)


# ==============================================================================
# RESUMEN DE COMPLEJIDAD — MEJOR CASO (notación Big-Omega, Ω)
# Archivo analizado: algoritmos.py
# ==============================================================================
#
# raizCuadrada (línea 1)
#   Suma de complejidades : Ω(1) + Ω(1) + Ω(log n) + Ω(log n) + Ω(log n) + Ω(1)
#   Términos agrupados    : 3·Ω(1) + 3·Ω(log n)
#   Mayor grado           : Ω(log n)
#
# factorial (línea 12)
#   Suma de complejidades : Ω(1) + Ω(n) + Ω(n) + Ω(1)
#   Términos agrupados    : 2·Ω(1) + 2·Ω(n)
#   Mayor grado           : Ω(n)
#
# burbuja (línea 21)
#   Suma de complejidades : Ω(1) + Ω(n) + Ω(n²) + Ω(n²) + Ω(n²) + Ω(1)
#   Términos agrupados    : 2·Ω(1) + 1·Ω(n) + 3·Ω(n²)
#   Mayor grado           : Ω(n²)
#
# ordenacionBinaria (línea 30)
#   Suma de complejidades : Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1)
#   Términos agrupados    : 9·Ω(1)
#   Mayor grado           : Ω(1)
#
# ------------------------------------------------------------------------------
# PROGRAMA COMPLETO
#   Suma de complejidades : Ω(log n) + Ω(n) + Ω(n²) + Ω(1)
#   Términos agrupados    : 16·Ω(1) + 3·Ω(log n) + 3·Ω(n) + 3·Ω(n²)
#   Mayor grado           : Ω(n²)  →  burbuja
#
# Las líneas marcadas como «no cuenta en el mejor caso» quedan fuera de la suma.
# ==============================================================================
