"""Catálogo de algoritmos de ordenamiento para el benchmark.

Cada función recibe una lista, **no la modifica** (trabaja sobre una copia,
porque `metricas.medir` ejecuta el algoritmo dos veces con la misma entrada) y
devuelve (lista ordenada, comparaciones, intercambios/escrituras).

Ordenar es un problema en **P**: hay algoritmos O(n log n) por comparaciones
(y ese es también el límite inferior para ellos). El ordenamiento por
permutaciones se incluye a propósito como contraste: resuelve el mismo
problema por fuerza bruta en O(n · n!), tiempo exponencial.
"""

import heapq
from itertools import permutations

Numero = int | float
Resultado = tuple[list[Numero], int, int]

# Límites para que una petición no deje colgado al servidor.
MAX_N = 50_000
MAX_N_CUADRATICO = 3_000
MAX_N_PERMUTACIONES = 8
MAX_RANGO_CONTEO = 1_000_000


def burbuja(datos: list[Numero]) -> Resultado:
    a = list(datos)
    comparaciones = intercambios = 0
    for i in range(len(a) - 1, 0, -1):
        hubo_intercambio = False
        for j in range(i):
            comparaciones += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                intercambios += 1
                hubo_intercambio = True
        if not hubo_intercambio:  # ya está ordenada: mejor caso O(n)
            break
    return a, comparaciones, intercambios


def seleccion(datos: list[Numero]) -> Resultado:
    a = list(datos)
    comparaciones = intercambios = 0
    for i in range(len(a) - 1):
        minimo = i
        for j in range(i + 1, len(a)):
            comparaciones += 1
            if a[j] < a[minimo]:
                minimo = j
        if minimo != i:
            a[i], a[minimo] = a[minimo], a[i]
            intercambios += 1
    return a, comparaciones, intercambios


def insercion(datos: list[Numero]) -> Resultado:
    a = list(datos)
    comparaciones = escrituras = 0
    for i in range(1, len(a)):
        actual = a[i]
        j = i - 1
        while j >= 0:
            comparaciones += 1
            if a[j] <= actual:
                break
            a[j + 1] = a[j]
            escrituras += 1
            j -= 1
        a[j + 1] = actual
    return a, comparaciones, escrituras


def merge_sort(datos: list[Numero]) -> Resultado:
    contador = [0, 0]  # comparaciones, escrituras

    def ordenar(a: list[Numero]) -> list[Numero]:
        if len(a) <= 1:
            return a
        mitad = len(a) // 2
        izq, der = ordenar(a[:mitad]), ordenar(a[mitad:])
        mezcla = []
        i = j = 0
        while i < len(izq) and j < len(der):
            contador[0] += 1
            if izq[i] <= der[j]:
                mezcla.append(izq[i])
                i += 1
            else:
                mezcla.append(der[j])
                j += 1
        mezcla += izq[i:] + der[j:]
        contador[1] += len(mezcla)
        return mezcla

    return ordenar(list(datos)), contador[0], contador[1]


def quick_sort(datos: list[Numero]) -> Resultado:
    """Partición de Hoare con pivote central, iterativo (pila explícita) para
    no depender del límite de recursión de Python."""
    a = list(datos)
    comparaciones = intercambios = 0
    pendientes = [(0, len(a) - 1)]
    while pendientes:
        bajo, alto = pendientes.pop()
        if bajo >= alto:
            continue
        pivote = a[(bajo + alto) // 2]
        i, j = bajo, alto
        while i <= j:
            while True:
                comparaciones += 1
                if a[i] >= pivote:
                    break
                i += 1
            while True:
                comparaciones += 1
                if a[j] <= pivote:
                    break
                j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                intercambios += 1
                i += 1
                j -= 1
        pendientes.append((bajo, j))
        pendientes.append((i, alto))
    return a, comparaciones, intercambios


def heap_sort(datos: list[Numero]) -> Resultado:
    a = list(datos)
    n = len(a)
    comparaciones = intercambios = 0

    def hundir(raiz: int, fin: int) -> None:
        nonlocal comparaciones, intercambios
        while 2 * raiz + 1 < fin:
            hijo = 2 * raiz + 1
            if hijo + 1 < fin:
                comparaciones += 1
                if a[hijo + 1] > a[hijo]:
                    hijo += 1
            comparaciones += 1
            if a[raiz] >= a[hijo]:
                return
            a[raiz], a[hijo] = a[hijo], a[raiz]
            intercambios += 1
            raiz = hijo

    for i in range(n // 2 - 1, -1, -1):  # construir el montículo máximo: O(n)
        hundir(i, n)
    for fin in range(n - 1, 0, -1):  # sacar el máximo n − 1 veces: O(n log n)
        a[0], a[fin] = a[fin], a[0]
        intercambios += 1
        hundir(0, fin)
    return a, comparaciones, intercambios


def counting_sort(datos: list[Numero]) -> Resultado:
    """No compara elementos: cuenta cuántas veces aparece cada valor. Solo
    sirve para enteros en un rango k = max − min + 1 razonable."""
    if not datos:
        return [], 0, 0
    minimo, maximo = int(min(datos)), int(max(datos))
    conteo = [0] * (maximo - minimo + 1)
    for x in datos:
        conteo[int(x) - minimo] += 1
    salida = []
    for desplazamiento, veces in enumerate(conteo):
        salida.extend([desplazamiento + minimo] * veces)
    return salida, 0, len(salida)


def permutaciones(datos: list[Numero]) -> Resultado:
    """Fuerza bruta: prueba permutaciones hasta encontrar una ordenada.
    Verificar cada candidata es O(n) (como un certificado de NP); lo caro es
    que hay n! candidatas."""
    comparaciones = probadas = 0
    for candidata in permutations(datos):
        probadas += 1
        for i in range(len(candidata) - 1):
            comparaciones += 1
            if candidata[i] > candidata[i + 1]:
                break
        else:
            return list(candidata), comparaciones, probadas
    return list(datos), comparaciones, probadas


# clave -> función y metadatos teóricos
CATALOGO: dict[str, dict] = {
    "burbuja": {
        "funcion": burbuja,
        "nombre": "Burbuja (Bubble sort)",
        "mejor": "Ω(n)",
        "promedio": "Θ(n²)",
        "peor": "O(n²)",
        "espacio": "O(1) adicional (in-place)",
        "estable": True,
        "clase": "P (cuadrático)",
        "max_n": MAX_N_CUADRATICO,
        "idea": "Recorre la lista intercambiando pares adyacentes desordenados; en cada "
        "pasada el mayor 'flota' a su lugar. Si una pasada no intercambia nada, termina.",
    },
    "seleccion": {
        "funcion": seleccion,
        "nombre": "Selección (Selection sort)",
        "mejor": "Ω(n²)",
        "promedio": "Θ(n²)",
        "peor": "O(n²)",
        "espacio": "O(1) adicional (in-place)",
        "estable": False,
        "clase": "P (cuadrático)",
        "max_n": MAX_N_CUADRATICO,
        "idea": "Busca el mínimo de la parte no ordenada y lo coloca al inicio. Siempre "
        "hace n(n−1)/2 comparaciones, aunque la lista ya esté ordenada.",
    },
    "insercion": {
        "funcion": insercion,
        "nombre": "Inserción (Insertion sort)",
        "mejor": "Ω(n)",
        "promedio": "Θ(n²)",
        "peor": "O(n²)",
        "espacio": "O(1) adicional (in-place)",
        "estable": True,
        "clase": "P (cuadrático)",
        "max_n": MAX_N_CUADRATICO,
        "idea": "Toma cada elemento y lo inserta en su lugar dentro de la parte ya "
        "ordenada, desplazando a los mayores. Muy rápido en listas casi ordenadas.",
    },
    "merge": {
        "funcion": merge_sort,
        "nombre": "Mezcla (Merge sort)",
        "mejor": "Ω(n log n)",
        "promedio": "Θ(n log n)",
        "peor": "O(n log n)",
        "espacio": "O(n) adicional",
        "estable": True,
        "clase": "P (n log n)",
        "max_n": MAX_N,
        "idea": "Divide y vencerás: parte la lista a la mitad, ordena cada mitad y las "
        "mezcla. T(n) = 2T(n/2) + O(n) = O(n log n) por el teorema maestro.",
    },
    "quick": {
        "funcion": quick_sort,
        "nombre": "Rápido (Quick sort)",
        "mejor": "Ω(n log n)",
        "promedio": "Θ(n log n)",
        "peor": "O(n²)",
        "espacio": "O(log n) adicional (pila)",
        "estable": False,
        "clase": "P (n log n en promedio)",
        "max_n": MAX_N,
        "idea": "Divide y vencerás: elige un pivote y parte la lista en menores y "
        "mayores que él. Si los pivotes parten mal (siempre el extremo), cae a O(n²).",
    },
    "heap": {
        "funcion": heap_sort,
        "nombre": "Montículo (Heap sort)",
        "mejor": "Ω(n log n)",
        "promedio": "Θ(n log n)",
        "peor": "O(n log n)",
        "espacio": "O(1) adicional (in-place)",
        "estable": False,
        "clase": "P (n log n)",
        "max_n": MAX_N,
        "idea": "Construye un montículo máximo en O(n) y extrae el máximo n − 1 veces, "
        "cada extracción en O(log n).",
    },
    "counting": {
        "funcion": counting_sort,
        "nombre": "Conteo (Counting sort)",
        "mejor": "Ω(n + k)",
        "promedio": "Θ(n + k)",
        "peor": "O(n + k)",
        "espacio": "O(n + k) adicional",
        "estable": True,
        "clase": "P (lineal en n + k)",
        "max_n": MAX_N,
        "idea": "No compara: cuenta cuántas veces aparece cada valor y los reescribe en "
        "orden. Rompe la cota Ω(n log n) porque no es por comparaciones; solo enteros.",
    },
    "permutaciones": {
        "funcion": permutaciones,
        "nombre": "Fuerza bruta por permutaciones (Permutation sort)",
        "mejor": "Ω(n)",
        "promedio": "Θ(n · n!)",
        "peor": "O(n · n!)",
        "espacio": "O(n) adicional",
        "estable": False,
        "clase": "Exponencial (fuerza bruta)",
        "max_n": MAX_N_PERMUTACIONES,
        "idea": "Genera permutaciones hasta dar con una ordenada. Verificar cada una es "
        "O(n), pero hay n! candidatas: ilustra por qué la fuerza bruta no escala.",
    },
}


def metadatos(clave: str) -> dict:
    info = CATALOGO[clave]
    return {
        "clave": clave,
        "algoritmo": info["nombre"],
        "complejidad": {"mejor": info["mejor"], "promedio": info["promedio"], "peor": info["peor"]},
        "espacio": info["espacio"],
        "estable": info["estable"],
        "clase": info["clase"],
    }


def validar(algoritmos: list[str], datos: list[Numero]) -> None:
    """Lanza ValueError si algún algoritmo no admite estos datos."""
    n = len(datos)
    for clave in algoritmos:
        info = CATALOGO[clave]
        if n > info["max_n"]:
            raise ValueError(
                f"{info['nombre']} admite hasta {info['max_n']} elementos "
                f"(se pidieron {n}): su costo es {info['peor']}."
            )
    if "counting" in algoritmos and datos:
        if any(isinstance(x, float) and not x.is_integer() for x in datos):
            raise ValueError("Counting sort solo ordena enteros.")
        rango = int(max(datos)) - int(min(datos)) + 1
        if rango > MAX_RANGO_CONTEO:
            raise ValueError(
                f"Counting sort necesita un arreglo del tamaño del rango de valores "
                f"(k = {rango}); el máximo permitido es {MAX_RANGO_CONTEO}."
            )
