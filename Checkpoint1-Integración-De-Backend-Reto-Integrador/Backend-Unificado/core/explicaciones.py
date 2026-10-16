"""Capa de interpretación y explicabilidad.

Cada endpoint agrega a su respuesta un campo `explicacion`: un texto que
describe qué pasó con *esos* datos (el proceso) y la base teórica que lo
sustenta, para que un usuario no especializado entienda el resultado.

`TEORIA` guarda la base teórica de cada operación o algoritmo; las funciones
de abajo la combinan con los datos concretos del resultado.
"""

from core.automatas import mostrar_cadena

TEORIA: dict[str, str] = {
    # Módulo 1: cadenas y lenguajes
    "concatenar": "La concatenación de dos cadenas w·v pone los símbolos de v después de "
    "los de w; |wv| = |w| + |v| y λ es su elemento neutro (wλ = w).",
    "unir": "Concatenar varias cadenas en orden es aplicar la concatenación de forma "
    "asociativa: (w₁w₂)w₃ = w₁(w₂w₃).",
    "potencia": "La potencia wⁿ es w concatenada consigo misma n veces; por definición "
    "w⁰ = λ (la cadena vacía) y |wⁿ| = n·|w|.",
    "union": "Un lenguaje es un conjunto de cadenas. L ∪ M contiene las cadenas que están "
    "en L, en M o en ambos.",
    "interseccion": "L ∩ M contiene solo las cadenas que pertenecen a ambos lenguajes.",
    "diferencia": "L − M contiene las cadenas de L que no están en M.",
    "concatenacion": "LM = {wv : w ∈ L, v ∈ M}: cada cadena de L seguida de cada cadena de "
    "M, por lo que |LM| ≤ |L|·|M|.",
    "complemento": "El complemento L̄ = Σ* − L son todas las cadenas sobre el alfabeto que "
    "no están en L. Σ* es infinito, así que se acota a una longitud máxima.",
    "clausura_kleene": "La clausura de Kleene L* = L⁰ ∪ L¹ ∪ L² ∪ … reúne todas las "
    "concatenaciones de cero o más cadenas de L; siempre contiene λ y es infinita si L "
    "tiene alguna cadena no vacía, por eso se listan solo los primeros elementos.",
    "AFD": "Un AFD M = (Q, Σ, δ, q₀, F) tiene exactamente un estado siguiente por símbolo. "
    "Una cadena w se acepta si la función de transición extendida δ*(q₀, w) termina en un "
    "estado de F.",
    "AFND": "En un AFND δ devuelve un conjunto de estados: el autómata 'está' en varios "
    "estados a la vez. Una cadena se acepta si el conjunto alcanzado contiene al menos un "
    "estado final.",
    "AFND-λ": "En un AFND-λ (AFND-ε) también hay transiciones λ, que se toman sin leer "
    "símbolos. Antes y después de cada símbolo se calcula la clausura-λ: todos los estados "
    "alcanzables solo con λ. Se acepta si el conjunto final contiene un estado de F.",
    # Módulo 2: grafos
    "bfs": "BFS es búsqueda no informada: explora por niveles con una cola FIFO. Es "
    "completa y encuentra la ruta con menos aristas, pero ignora los pesos. Costo "
    "O(V + E).",
    "dfs": "DFS es búsqueda no informada: avanza por una rama con una pila LIFO hasta el "
    "fondo y luego retrocede (backtracking). Usa poca memoria, pero la ruta que encuentra "
    "depende del orden de los vecinos y no es óptima. Costo O(V + E).",
    "hill-climbing": "Hill-Climbing es búsqueda local: solo guarda el nodo actual y se "
    "mueve al vecino con mejor heurística mientras mejore. Es muy barato, pero es "
    "incompleto: puede atorarse en óptimos locales o mesetas aunque exista camino.",
    "greedy": "La búsqueda voraz expande el nodo con menor h(n) (f(n) = h(n)): va hacia "
    "donde la heurística dice que está el destino. Es rápida pero no garantiza la ruta "
    "de menor costo. O(b^m) en el peor caso.",
    "astar": "A* expande el nodo con menor f(n) = g(n) + h(n): costo real acumulado más "
    "la estimación de lo que falta. Si h nunca sobreestima (admisible), la primera vez "
    "que llega al destino lo hace por la ruta de menor costo. O(b^d).",
    "dijkstra": "Dijkstra resuelve el camino de menor costo con pesos no negativos: fija "
    "siempre el nodo de la frontera con menor distancia acumulada y relaja sus aristas. "
    "Es un problema en P: O((V + E) log V) con cola de prioridad.",
    "tsp": "El agente viajero (TSP) busca el ciclo más barato que visita todos los nodos "
    "una vez. Es NP-difícil: Held-Karp da el óptimo con programación dinámica en "
    "O(n²·2ⁿ), tiempo exponencial.",
    "tsp-greedy": "La heurística del vecino más cercano resuelve el TSP de forma "
    "aproximada en O(n²): avanza siempre por la arista más barata a un nodo no visitado. "
    "Es polinomial, pero no garantiza el óptimo.",
    "generar": "El generador crea un ciclo que pasa por todos los nodos (garantiza que el "
    "grafo es conexo y que el TSP tiene solución) y agrega aristas al azar según la "
    "densidad. Con la misma semilla se obtiene el mismo grafo.",
    # Módulo 3: complejidad y benchmark
    "complejidad": "El análisis asintótico cuenta cuántas veces se ejecuta cada línea en "
    "función del tamaño n de la entrada. Big-O acota el peor caso por arriba y Big-Ω el "
    "mejor caso por abajo; en una suma domina el término de mayor grado.",
    "clases": "P son los problemas que se resuelven en tiempo polinomial; NP, los que se "
    "verifican en tiempo polinomial dado un certificado; NSPACE(f(n)), los que una máquina "
    "no determinista resuelve con f(n) de memoria. Ordenar está en P (O(n log n)) y en "
    "espacio O(n), así que también está en NP y en NSPACE(n). Verificar que una lista "
    "está ordenada toma O(n).",
}


def _cadena(w: str) -> str:
    return mostrar_cadena(w) if w == "" else f"'{w}'"


def _conjunto(elementos: list[str], maximo: int = 8) -> str:
    vistos = [_cadena(w) for w in elementos[:maximo]]
    if len(elementos) > maximo:
        vistos.append("…")
    return "{" + ", ".join(vistos) + "}"


# ---------------------------------------------------------------------------
# Módulo 1
# ---------------------------------------------------------------------------


def cadena(operacion: str, resultado: str, **datos) -> str:
    if operacion == "concatenar":
        proceso = (
            f"{_cadena(datos['a'])} · {_cadena(datos['b'])} = {_cadena(resultado)} "
            f"(longitud {len(datos['a'])} + {len(datos['b'])} = {len(resultado)})."
        )
    elif operacion == "unir":
        proceso = (
            f"Se concatenaron {len(datos['cadenas'])} cadenas en orden: "
            f"{' · '.join(_cadena(c) for c in datos['cadenas']) or 'λ'} = {_cadena(resultado)}."
        )
    else:
        proceso = (
            f"{_cadena(datos['cadena'])}^{datos['n']} = {_cadena(resultado)} "
            f"(longitud {datos['n']} · {len(datos['cadena'])} = {len(resultado)})."
        )
    return f"{proceso} {TEORIA[operacion]}"


def lenguaje(operacion: str, resultado: list[str], **datos) -> str:
    L, M = datos.get("L", []), datos.get("M")
    entrada = f"L = {_conjunto(L)}" + (f" y M = {_conjunto(M)}" if M is not None else "")
    proceso = f"Con {entrada} se obtuvieron {len(resultado)} cadena(s): {_conjunto(resultado)}."
    return f"{proceso} {TEORIA[operacion]}"


def _tipo_automata(tipo: str) -> str:
    return "AFND-λ" if "λ" in tipo else ("AFND" if tipo.startswith("AFND") else "AFD")


def automata_cadena(tipo: str, estado_inicial: str, r: dict) -> str:
    """Explicación de una sola cadena evaluada."""
    w = _cadena(r["cadena"])
    if tipo == "AFD":
        if r["estado_final_alcanzado"] is None:
            return f"{w} se rechaza: {r['motivo']}"
        q = r["estado_final_alcanzado"]
        if r["aceptada"]:
            return f"{w} ∈ L(M) porque δ*({estado_inicial}, {w}) = {q} y {q} ∈ F."
        return f"{w} ∉ L(M) porque δ*({estado_inicial}, {w}) = {q} y {q} ∉ F."

    alcanzados = "{" + ", ".join(r["estados_alcanzados"]) + "}"
    if r["aceptada"]:
        return (
            f"{w} ∈ L(M): el conjunto alcanzado {alcanzados} contiene el/los estado(s) "
            f"final(es) {', '.join(r['estados_finales_alcanzados'])}."
        )
    return f"{w} ∉ L(M): {r['motivo']}"


def automata(tipo: str, resultados: list[dict]) -> str:
    aceptadas = [_cadena(r["cadena"]) for r in resultados if r["aceptada"]]
    rechazadas = [_cadena(r["cadena"]) for r in resultados if not r["aceptada"]]
    proceso = (
        f"Se evaluaron {len(resultados)} cadena(s) en un {tipo}: "
        f"aceptadas {', '.join(aceptadas) or 'ninguna'}; "
        f"rechazadas {', '.join(rechazadas) or 'ninguna'}."
    )
    return f"{proceso} {TEORIA[_tipo_automata(tipo)]}"


# ---------------------------------------------------------------------------
# Módulo 2
# ---------------------------------------------------------------------------


def algoritmo_grafo(clave: str, resultado: dict, heuristica: dict | None = None) -> str:
    proceso = resultado["motivo"]
    if resultado.get("ruta"):
        proceso += f" Ruta: {' → '.join(resultado['ruta'])}."
    if heuristica is not None:
        proceso += f" Heurística usada: {heuristica['formula']}."
    return f"{proceso} {TEORIA[clave]}"


def comparacion(resultado: dict) -> str:
    tabla = {fila["clave"]: fila for fila in resultado["tabla"]}
    partes = []
    if resultado["mejor"]:
        mejor = tabla[resultado["mejor"]]
        partes.append(
            f"La ruta más barata la dio {mejor['algoritmo']} (costo {mejor['costo']:g})."
        )
        caros = [
            f"{f['algoritmo']} ({f['costo']:g})"
            for f in resultado["tabla"]
            if f["costo"] is not None and f["costo"] > mejor["costo"]
        ]
        if caros:
            partes.append(f"Encontraron rutas más caras: {', '.join(caros)}.")
    sin_ruta = [f["algoritmo"] for f in resultado["tabla"] if not f["solucion"]]
    if sin_ruta:
        partes.append(f"No llegaron al destino: {', '.join(sin_ruta)}.")
    partes.append(f"El más rápido fue {tabla[resultado['mas_rapido']]['algoritmo']}.")
    partes.append(
        "Todos se ejecutaron con el mismo grafo. Dijkstra y A* (con heurística admisible) "
        "garantizan el costo mínimo; BFS minimiza el número de aristas; DFS, la búsqueda "
        "voraz y Hill-Climbing son más baratos pero no garantizan el óptimo."
    )
    return " ".join(partes)


# ---------------------------------------------------------------------------
# Módulo 3
# ---------------------------------------------------------------------------


def complejidad(resultado: dict) -> str:
    programa = resultado["programa"]
    caso = "peor" if resultado["caso"] == "peor" else "mejor"
    proceso = (
        f"En el {caso} caso el programa es {programa['complejidad']}: lo determinan "
        f"{', '.join(programa['funciones_mayor_grado'])}."
    )
    return f"{proceso} {TEORIA['complejidad']}"


def ordenamiento(n: int, resultados: list[dict], ranking: list[str]) -> str:
    por_clave = {r["clave"]: r for r in resultados}
    rapido, lento = por_clave[ranking[0]], por_clave[ranking[-1]]
    proceso = (
        f"Se ordenaron los mismos {n} elementos con {len(resultados)} algoritmos. "
        f"El más rápido fue {rapido['algoritmo']} ({rapido['tiempo_ms']:g} ms, "
        f"{rapido['complejidad']['promedio']}) y el más lento {lento['algoritmo']} "
        f"({lento['tiempo_ms']:g} ms, {lento['complejidad']['promedio']})."
    )
    return f"{proceso} {TEORIA['clases']}"


def escalabilidad(series: dict[str, list[dict]], nombres: dict[str, str]) -> str:
    partes = []
    for clave, puntos in series.items():
        if len(puntos) >= 2 and puntos[0]["tiempo_ms"] > 0:
            factor_n = puntos[-1]["n"] / puntos[0]["n"]
            factor_t = puntos[-1]["tiempo_ms"] / puntos[0]["tiempo_ms"]
            partes.append(
                f"{nombres[clave]}: n creció ×{factor_n:g} y el tiempo ×{factor_t:.1f}"
            )
    proceso = (
        "Crecimiento observado: " + "; ".join(partes) + ". "
        if partes
        else ""
    )
    return (
        f"{proceso}Si n se multiplica por c, un algoritmo O(n²) tarda ~c² veces más y uno "
        f"O(n log n) un poco más de c veces: esa diferencia es la que muestra la gráfica. "
        f"{TEORIA['clases']}"
    )
