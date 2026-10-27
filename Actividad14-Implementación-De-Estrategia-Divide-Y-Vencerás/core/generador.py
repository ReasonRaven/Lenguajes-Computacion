"""Generador de enteros aleatorios de exactamente N dígitos."""

import random


def generar(n: int, semilla: int | None = None) -> tuple[str, str]:
    """Dos enteros de `n` dígitos (el primero nunca es 0). Con la misma
    semilla se obtienen siempre los mismos números."""
    aleatorio = random.Random(semilla)

    def numero() -> str:
        primero = str(aleatorio.randint(1, 9))
        return primero + "".join(str(aleatorio.randint(0, 9)) for _ in range(n - 1))

    return numero(), numero()
