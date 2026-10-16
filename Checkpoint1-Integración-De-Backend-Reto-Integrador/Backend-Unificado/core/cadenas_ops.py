def concatenar(a: str, b: str) -> str:
    return a + b


def unir(cadenas: list[str]) -> str:
    return "".join(cadenas)


def potencia(cadena: str, n: int) -> str:
    if n < 0:
        raise ValueError("n debe ser >= 0")
    return cadena * n
