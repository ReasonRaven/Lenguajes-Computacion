"""Medición de tiempo y memoria de un algoritmo.

El algoritmo se ejecuta dos veces con la misma entrada:

1. Con `time.perf_counter` para el tiempo, sin nada más activo.
2. Con `tracemalloc` para la memoria: el pico de bytes reservados por Python
   mientras corre (estructuras auxiliares, colas, tablas, rutas...). No
   incluye el grafo de entrada, que ya existía antes de llamar al algoritmo.

Se separan porque `tracemalloc` intercepta cada reserva de memoria y hace más
lento el código; si se midieran juntos, el tiempo reportado estaría inflado.
Los algoritmos son deterministas, así que las dos ejecuciones hacen el mismo
trabajo.
"""

import threading
import time
import tracemalloc
from typing import Any, Callable

# tracemalloc es global al proceso; FastAPI atiende los endpoints síncronos en
# un pool de hilos, así que dos mediciones simultáneas se estorbarían.
_candado = threading.Lock()


def medir(algoritmo: Callable[..., Any], *args: Any) -> tuple[Any, float, float]:
    """Devuelve (resultado, tiempo en ms, pico de memoria en KB)."""
    with _candado:
        inicio = time.perf_counter()
        resultado = algoritmo(*args)
        tiempo_ms = (time.perf_counter() - inicio) * 1000

        tracemalloc.start()
        try:
            algoritmo(*args)
            _, pico = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()

    return resultado, round(tiempo_ms, 4), round(pico / 1024, 3)
