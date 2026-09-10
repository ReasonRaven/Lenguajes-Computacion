"""Utilidades compartidas por los evaluadores de AFD y AFND.

Una tabla de transición se representa como un diccionario donde la llave es el
estado y el valor es otro diccionario símbolo -> destino(s). El símbolo lambda
(transición vacía, solo válida en AFND) puede escribirse de varias formas y
aquí se normaliza siempre a "λ".
"""

import re

LAMBDA = "λ"
LLAVES_LAMBDA = {"λ", "lambda", "ε", "epsilon", "e", ""}


class AutomataInvalido(ValueError):
    """La tabla de transición no describe un autómata bien formado."""


def es_lambda(simbolo: str) -> bool:
    return simbolo.strip().lower() in LLAVES_LAMBDA


def orden_natural(nombre: str) -> tuple:
    """Ordena q0, q1, q2, q10 en ese orden (y no q0, q1, q10, q2)."""
    partes = re.split(r"(\d+)", nombre)
    return tuple(int(p) if p.isdigit() else p for p in partes)


def ordenar(nombres) -> list[str]:
    return sorted(set(nombres), key=orden_natural)


def destinos(celda) -> list[str]:
    """Normaliza una celda de la tabla a lista de estados destino.

    Acepta tanto la forma determinista ("q1") como la no determinista
    (["q1", "q2"]); una celda vacía o nula significa transición indefinida.
    """
    if celda is None:
        return []
    if isinstance(celda, str):
        return [celda] if celda else []
    return [str(estado) for estado in celda if estado]


def estados_de(tabla: dict) -> list[str]:
    """Estados totales: los declarados como fila más los que aparecen como
    destino (aunque no tengan fila propia, p. ej. un estado de aceptación)."""
    encontrados = set(tabla)
    for transiciones in tabla.values():
        for celda in transiciones.values():
            encontrados.update(destinos(celda))
    return ordenar(encontrados)


def alfabeto_de(tabla: dict) -> list[str]:
    """Alfabeto Σ: todos los símbolos de la tabla excepto λ, que no forma
    parte del alfabeto de entrada."""
    simbolos = {
        simbolo
        for transiciones in tabla.values()
        for simbolo in transiciones
        if not es_lambda(simbolo)
    }
    return sorted(simbolos)


def normalizar_tabla(tabla: dict) -> dict[str, dict[str, list[str]]]:
    """Deja la tabla con celdas siempre en forma de lista y la llave lambda
    escrita como "λ", agregando filas vacías para los estados que solo
    aparecen como destino."""
    normalizada: dict[str, dict[str, list[str]]] = {}
    for estado, transiciones in tabla.items():
        fila: dict[str, list[str]] = {}
        for simbolo, celda in transiciones.items():
            llave = LAMBDA if es_lambda(simbolo) else simbolo
            fila.setdefault(llave, [])
            fila[llave].extend(d for d in destinos(celda) if d not in fila[llave])
        normalizada[estado] = fila
    for estado in estados_de(tabla):
        normalizada.setdefault(estado, {})
    return normalizada


def tiene_lambda(tabla: dict[str, dict[str, list[str]]]) -> bool:
    return any(fila.get(LAMBDA) for fila in tabla.values())


def validar(
    tabla: dict[str, dict[str, list[str]]],
    estado_inicial: str,
    estados_finales: list[str],
    permitir_lambda: bool,
) -> None:
    """Verifica que el autómata esté bien formado; lanza AutomataInvalido."""
    if not tabla:
        raise AutomataInvalido("La tabla de transición está vacía.")

    conocidos = set(estados_de(tabla))

    if estado_inicial not in conocidos:
        raise AutomataInvalido(
            f"El estado inicial '{estado_inicial}' no aparece en la tabla de transición."
        )

    desconocidos = [e for e in estados_finales if e not in conocidos]
    if desconocidos:
        raise AutomataInvalido(
            "Estado(s) final(es) que no aparecen en la tabla de transición: "
            + ", ".join(desconocidos)
        )

    if not permitir_lambda and tiene_lambda(tabla):
        raise AutomataInvalido(
            "Un AFD no admite transiciones λ; usa el endpoint /afnd/evaluar."
        )


def descripcion(tabla: dict[str, dict[str, list[str]]]) -> str:
    """Distingue un AFND con transiciones λ de uno sin ellas."""
    return "AFND-λ" if tiene_lambda(tabla) else "AFND"


def formato_conjunto(estados) -> str:
    """{q0, q1} — o ∅ si el conjunto está vacío."""
    ordenados = ordenar(estados)
    return "{" + ", ".join(ordenados) + "}" if ordenados else "∅"


def mostrar_cadena(cadena: str) -> str:
    return cadena if cadena else LAMBDA
