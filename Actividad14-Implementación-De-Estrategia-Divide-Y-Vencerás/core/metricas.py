"""Medición de tiempo T(N) y espacio S(N) de un algoritmo.

Igual que en la Actividad 13, el algoritmo se ejecuta por separado para cada
métrica:

1. **Tiempo:** `time.perf_counter` alrededor de la llamada, sin nada más
   activo. Con 20 dígitos una multiplicación tarda microsegundos y una sola
   medición es muy ruidosa, así que se repite `repeticiones` veces y se
   reporta la **mediana**.
2. **Espacio:** `tracemalloc` registra cada reserva de memoria de Python
   durante una ejecución; se reporta el **pico** (el mayor total reservado a
   la vez): listas de dígitos temporales, mitades, sumas, el resultado... Las
   listas de entrada no cuentan, porque ya existían.

Se separan porque `tracemalloc` hace más lento el código que observa; medidos
juntos, el tiempo saldría inflado. Los algoritmos son deterministas, así que
todas las ejecuciones hacen exactamente el mismo trabajo.
"""

import statistics
import threading
import time
import tracemalloc
from typing import Any, Callable

# tracemalloc es global al proceso; FastAPI atiende los endpoints síncronos en
# un pool de hilos, así que dos mediciones simultáneas se estorbarían.
_candado = threading.Lock()


def medir(
    algoritmo: Callable[..., Any], *args: Any, repeticiones: int = 1
) -> tuple[Any, float, float]:
    """Devuelve (resultado, mediana del tiempo en ms, pico de memoria en KB)."""
    with _candado:
        tiempos = []
        for _ in range(repeticiones):
            inicio = time.perf_counter()
            resultado = algoritmo(*args)
            tiempos.append((time.perf_counter() - inicio) * 1000)

        tracemalloc.start()
        try:
            algoritmo(*args)
            _, pico = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

    return resultado, round(statistics.median(tiempos), 4), round(pico / 1024, 3)
