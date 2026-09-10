"""Evaluación de cadenas sobre un Autómata Finito Determinista."""

from core import automatas


def evaluar_cadena(
    tabla: dict[str, dict[str, list[str]]],
    estado_inicial: str,
    estados_finales: list[str],
    alfabeto: list[str],
    cadena: str,
) -> dict:
    """Recorre la cadena símbolo por símbolo y devuelve el resultado junto con
    la notación de configuraciones (q, w) ⊢ (q', w')."""
    actual = estado_inicial
    configuraciones = [f"({actual}, {automatas.mostrar_cadena(cadena)})"]
    transiciones: list[str] = []
    motivo: str | None = None

    for i, simbolo in enumerate(cadena):
        restante = cadena[i + 1 :]

        if simbolo not in alfabeto:
            motivo = f"El símbolo '{simbolo}' no pertenece al alfabeto Σ = {{{', '.join(alfabeto)}}}."
            configuraciones.append(f"(∅, {automatas.mostrar_cadena(restante)})")
            break

        siguientes = tabla.get(actual, {}).get(simbolo, [])
        if not siguientes:
            motivo = f"No hay transición definida para δ({actual}, {simbolo})."
            transiciones.append(f"δ({actual}, {simbolo}) = ∅")
            configuraciones.append(f"(∅, {automatas.mostrar_cadena(restante)})")
            break

        destino = siguientes[0]
        transiciones.append(f"δ({actual}, {simbolo}) = {destino}")
        actual = destino
        configuraciones.append(f"({actual}, {automatas.mostrar_cadena(restante)})")
    else:
        aceptada = actual in estados_finales
        return {
            "cadena": cadena,
            "cadena_mostrada": automatas.mostrar_cadena(cadena),
            "aceptada": aceptada,
            "estado_final_alcanzado": actual,
            "notacion": " ⊢ ".join(configuraciones),
            "transiciones": transiciones,
            "motivo": (
                f"Termina en {actual}, que es un estado de aceptación."
                if aceptada
                else f"Termina en {actual}, que no es un estado de aceptación."
            ),
        }

    return {
        "cadena": cadena,
        "cadena_mostrada": automatas.mostrar_cadena(cadena),
        "aceptada": False,
        "estado_final_alcanzado": None,
        "notacion": " ⊢ ".join(configuraciones),
        "transiciones": transiciones,
        "motivo": motivo,
    }


def evaluar(
    tabla: dict,
    estado_inicial: str,
    estados_finales: list[str],
    cadenas: list[str],
) -> dict:
    """Valida el AFD y evalúa todas las cadenas recibidas."""
    normalizada = automatas.normalizar_tabla(tabla)
    automatas.validar(normalizada, estado_inicial, estados_finales, permitir_lambda=False)

    estados = automatas.estados_de(tabla)
    alfabeto = automatas.alfabeto_de(tabla)

    ambiguos = [
        f"δ({estado}, {simbolo})"
        for estado, fila in normalizada.items()
        for simbolo, celda in fila.items()
        if len(celda) > 1
    ]
    if ambiguos:
        raise automatas.AutomataInvalido(
            "Un AFD debe tener a lo más un destino por celda; hay varios en: "
            + ", ".join(ambiguos)
        )

    return {
        "tipo": "AFD",
        "estados": estados,
        "alfabeto": alfabeto,
        "estado_inicial": estado_inicial,
        "estados_finales": automatas.ordenar(estados_finales),
        "resultados": [
            evaluar_cadena(normalizada, estado_inicial, estados_finales, alfabeto, cadena)
            for cadena in cadenas
        ],
    }
