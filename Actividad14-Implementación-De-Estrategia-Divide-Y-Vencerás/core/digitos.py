"""Enteros grandes como listas de dígitos.

Los dos algoritmos de multiplicación trabajan sobre listas de dígitos en base
10, **little-endian** (el dígito de las unidades primero):

    "1234"  ->  [4, 3, 2, 1]

Así el dígito i siempre vale `d[i] · 10^i`, sumar y restar recorren la lista de
izquierda a derecha arrastrando el acarreo, y multiplicar por `10^k` es
anteponer `k` ceros.

No se usa la multiplicación de enteros de Python con los números grandes: el
`*` nativo ya aplica Karatsuba internamente, así que usarlo invalidaría la
comparación. Solo se multiplican dígitos sueltos (0-9) entre sí.

El cero se representa como `[0]`; ninguna otra lista tiene ceros sobrantes al
final (ceros a la izquierda del número).
"""

Digitos = list[int]


def parsear(texto: str) -> tuple[bool, Digitos]:
    """Convierte "-00123" en (True, [3, 2, 1]). Lanza ValueError si el texto
    no es un entero en base 10."""
    texto = texto.strip()
    negativo = texto.startswith("-")
    cuerpo = texto[1:] if texto[:1] in "+-" else texto
    if not cuerpo or not all(c in "0123456789" for c in cuerpo):
        raise ValueError(f"'{texto}' no es un entero en base 10")
    digitos = quitar_ceros([int(c) for c in reversed(cuerpo)])
    return negativo and not es_cero(digitos), digitos


def formatear(negativo: bool, digitos: Digitos) -> str:
    """Operación inversa de `parsear`."""
    texto = "".join(str(d) for d in reversed(digitos))
    return "-" + texto if negativo and not es_cero(digitos) else texto


def quitar_ceros(d: Digitos) -> Digitos:
    """Elimina los ceros a la izquierda del número (al final de la lista)."""
    fin = len(d)
    while fin > 1 and d[fin - 1] == 0:
        fin -= 1
    return d[:fin] if fin else [0]


def es_cero(d: Digitos) -> bool:
    return d == [0]


def sumar(a: Digitos, b: Digitos) -> Digitos:
    """a + b, dígito a dígito con acarreo. O(n)."""
    if len(a) < len(b):
        a, b = b, a
    resultado = []
    acarreo = 0
    for i in range(len(a)):
        t = a[i] + (b[i] if i < len(b) else 0) + acarreo
        resultado.append(t % 10)
        acarreo = t // 10
    if acarreo:
        resultado.append(acarreo)
    return resultado


def restar(a: Digitos, b: Digitos) -> Digitos:
    """a − b, con préstamo. Requiere a ≥ b. O(n)."""
    resultado = []
    prestamo = 0
    for i in range(len(a)):
        t = a[i] - (b[i] if i < len(b) else 0) - prestamo
        prestamo = 1 if t < 0 else 0
        resultado.append(t + 10 if t < 0 else t)
    if prestamo:
        raise ValueError("restar: el sustraendo es mayor que el minuendo")
    return quitar_ceros(resultado)


def desplazar(d: Digitos, k: int) -> Digitos:
    """d · 10^k: antepone k ceros. O(n + k)."""
    return d if es_cero(d) else [0] * k + d
