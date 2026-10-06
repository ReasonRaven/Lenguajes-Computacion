"""Evaluación de cadenas sobre un Autómata Finito No Determinista (con o sin
transiciones λ). La evaluación se hace por conjuntos de estados: en cada paso
se calcula la clausura-λ del conjunto alcanzado."""

from collections import deque

from core import automatas
from core.automatas import LAMBDA


def clausura_lambda(tabla: dict[str, dict[str, list[str]]], estados) -> set[str]:
    """Todos los estados alcanzables desde `estados` usando solo transiciones λ."""
    alcanzables = set(estados)
    pendientes = deque(alcanzables)
    while pendientes:
        estado = pendientes.popleft()
        for destino in tabla.get(estado, {}).get(LAMBDA, []):
            if destino not in alcanzables:
                alcanzables.add(destino)
                pendientes.append(destino)
    return alcanzables


def mover(tabla: dict[str, dict[str, list[str]]], estados, simbolo: str) -> set[str]:
    """Conjunto de estados alcanzables leyendo `simbolo` desde `estados`."""
    return {
        destino
        for estado in estados
        for destino in tabla.get(estado, {}).get(simbolo, [])
    }


def camino_de_aceptacion(
    tabla: dict[str, dict[str, list[str]]],
    estado_inicial: str,
    estados_finales: list[str],
    cadena: str,
) -> list[str] | None:
    """Busca en anchura un camino concreto que acepte la cadena y lo devuelve
    como notación q0 --a--> q1 --λ--> q2. Devuelve None si no existe."""
    inicio = (estado_inicial, 0)
    padres: dict[tuple[str, int], tuple[tuple[str, int], str] | None] = {inicio: None}
    cola = deque([inicio])
    meta = None

    while cola:
        nodo = cola.popleft()
        estado, i = nodo
        if i == len(cadena) and estado in estados_finales:
            meta = nodo
            break
        transiciones = tabla.get(estado, {})
        vecinos = [((destino, i), LAMBDA) for destino in transiciones.get(LAMBDA, [])]
        if i < len(cadena):
            vecinos += [
                ((destino, i + 1), cadena[i])
                for destino in transiciones.get(cadena[i], [])
            ]
        for vecino, etiqueta in vecinos:
            if vecino not in padres:
                padres[vecino] = (nodo, etiqueta)
                cola.append(vecino)

    if meta is None:
        return None

    pasos: list[str] = []
    nodo = meta
    while padres[nodo] is not None:
        anterior, etiqueta = padres[nodo]
        pasos.append(f" --{etiqueta}--> {nodo[0]}")
        nodo = anterior
    pasos.append(estado_inicial)
    return "".join(reversed(pasos))


def evaluar_cadena(
    tabla: dict[str, dict[str, list[str]]],
    estado_inicial: str,
    estados_finales: list[str],
    alfabeto: list[str],
    cadena: str,
) -> dict:
    actual = clausura_lambda(tabla, {estado_inicial})
    pasos = [automatas.formato_conjunto(actual)]
    transiciones: list[str] = []
    motivo: str | None = None

    for i, simbolo in enumerate(cadena):
        if simbolo not in alfabeto:
            motivo = f"El símbolo '{simbolo}' no pertenece al alfabeto Σ = {{{', '.join(alfabeto)}}}."
            pasos.append(f"--{simbolo}--> ∅")
            actual = set()
            break

        siguiente = clausura_lambda(tabla, mover(tabla, actual, simbolo))
        transiciones.append(
            f"δ({automatas.formato_conjunto(actual)}, {simbolo}) = "
            f"{automatas.formato_conjunto(siguiente)}"
        )
        pasos.append(f"--{simbolo}--> {automatas.formato_conjunto(siguiente)}")
        actual = siguiente
        if not actual:
            motivo = f"No hay transiciones desde ese conjunto al leer '{simbolo}'."
            break

    alcanzados = automatas.ordenar(actual & set(estados_finales))
    aceptada = bool(alcanzados)

    if motivo is None:
        motivo = (
            "El conjunto final "
            f"{automatas.formato_conjunto(actual)} contiene el/los estado(s) de "
            f"aceptación {', '.join(alcanzados)}."
            if aceptada
            else f"El conjunto final {automatas.formato_conjunto(actual)} no contiene estados de aceptación."
        )

    return {
        "cadena": cadena,
        "cadena_mostrada": automatas.mostrar_cadena(cadena),
        "aceptada": aceptada,
        "estados_alcanzados": automatas.ordenar(actual),
        "estados_finales_alcanzados": alcanzados,
        "notacion": " ".join(pasos),
        "transiciones": transiciones,
        "camino_aceptacion": (
            camino_de_aceptacion(tabla, estado_inicial, estados_finales, cadena)
            if aceptada
            else None
        ),
        "motivo": motivo,
    }


def evaluar(
    tabla: dict,
    estado_inicial: str,
    estados_finales: list[str],
    cadenas: list[str],
) -> dict:
    """Valida el AFND y evalúa todas las cadenas recibidas."""
    normalizada = automatas.normalizar_tabla(tabla)
    automatas.validar(normalizada, estado_inicial, estados_finales, permitir_lambda=True)

    return {
        "tipo": automatas.descripcion(normalizada),
        "estados": automatas.estados_de(tabla),
        "alfabeto": automatas.alfabeto_de(tabla),
        "estado_inicial": estado_inicial,
        "estados_finales": automatas.ordenar(estados_finales),
        "resultados": [
            evaluar_cadena(
                normalizada,
                estado_inicial,
                estados_finales,
                automatas.alfabeto_de(tabla),
                cadena,
            )
            for cadena in cadenas
        ],
    }
