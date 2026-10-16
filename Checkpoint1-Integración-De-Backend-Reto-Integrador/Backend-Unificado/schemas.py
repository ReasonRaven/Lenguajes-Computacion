"""Esquemas de entrada y salida (Pydantic) de los endpoints de grafos y benchmark.

La entrada acepta el grafo en tres formatos (lista de adyacencia, matriz de
adyacencia o vector de aristas) y se valida por completo antes de llegar a los
algoritmos: si algo no cuadra, FastAPI responde 422 con el motivo.
"""

from typing import Literal

from fastapi.openapi.models import Example
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from core import comparador, generador, grafos, ordenamiento, tsp


class GrafoRequest(BaseModel):
    """Campos comunes a todos los endpoints: el grafo en cualquiera de sus tres
    formatos y si es dirigido."""

    lista_adyacencia: dict[str, list[tuple[str, float]]] | None = Field(
        None,
        description="Lista de adyacencia con pesos: nodo -> [[vecino, peso], ...]. "
        "Es el formato del archivo de la actividad.",
    )
    matriz_adyacencia: list[list[float | None]] | None = Field(
        None,
        description="Matriz de adyacencia con pesos; la celda [i][j] es el peso de la "
        "arista nodos[i] → nodos[j]. 0 o null significa que no hay arista.",
    )
    nodos: list[str] | None = Field(
        None, description="Nombre de cada fila/columna de `matriz_adyacencia`."
    )
    aristas: list[tuple[str, str, float]] | None = Field(
        None, description="Vector de aristas: [[origen, destino, peso], ...]."
    )
    dirigido: bool = Field(
        True, description="Con `false` cada arista se recorre en ambos sentidos."
    )

    _grafo: grafos.Grafo = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def validar_grafo(self) -> "GrafoRequest":
        self._grafo = grafos.construir_grafo(
            self.lista_adyacencia,
            self.matriz_adyacencia,
            self.nodos,
            self.aristas,
            self.dirigido,
        )
        return self

    @property
    def grafo(self) -> grafos.Grafo:
        """El grafo ya normalizado a lista de adyacencia."""
        return self._grafo

    def _validar_nodo(self, campo: str) -> None:
        nodo = getattr(self, campo)
        if nodo not in self._grafo:
            raise ValueError(f"El {campo} '{nodo}' no es un nodo del grafo.")


class ConHeuristicaRequest(GrafoRequest):
    """Grafo + origen/destino + la heurística h(n) que usan la búsqueda voraz, A*
    y Hill-Climbing. El destino es opcional solo en la comparación (BFS/DFS sin
    destino calculan el alcance máximo)."""

    origen: str = Field(..., description="Nodo de inicio.")
    destino: str | None = Field(..., description="Nodo a alcanzar.")
    coordenadas: dict[str, tuple[float, float]] | None = Field(
        None,
        description="Posición [x, y] de cada nodo, para la heurística euclidiana.",
    )
    heuristica: Literal["euclidiana", "saltos"] | None = Field(
        None,
        description="`euclidiana` (requiere `coordenadas`) o `saltos`. Por defecto, "
        "euclidiana si se envían coordenadas y por saltos si no.",
    )

    @model_validator(mode="after")
    def validar_heuristica(self) -> "ConHeuristicaRequest":
        self._validar_nodo("origen")
        if self.destino is not None:
            self._validar_nodo("destino")

        if self.heuristica is None:
            self.heuristica = "euclidiana" if self.coordenadas else "saltos"
        if self.heuristica == "euclidiana":
            grafos.validar_coordenadas(self.grafo, self.coordenadas)
        return self

    def calcular_heuristica(self) -> tuple[dict[str, float], dict]:
        return grafos.calcular_heuristica(
            self.grafo, self.heuristica, self.coordenadas, self.destino
        )


class BusquedaRequest(ConHeuristicaRequest):
    destino: str = Field(..., description="Nodo a alcanzar.")
    limite_nodos: int | None = Field(
        None,
        ge=1,
        description="Máximo de nodos a visitar (expandir). Por defecto, el 80 % del "
        "número total de nodos, redondeado hacia arriba.",
    )

    @model_validator(mode="after")
    def validar_limite(self) -> "BusquedaRequest":
        if self.limite_nodos is None:
            self.limite_nodos = grafos.limite_por_defecto(len(self.grafo))
        return self


class HillClimbingRequest(ConHeuristicaRequest):
    destino: str = Field(..., description="Nodo a alcanzar.")


class Heuristica(BaseModel):
    tipo: Literal["euclidiana", "saltos"]
    formula: str
    escala: float = Field(
        ...,
        description="Euclidiana: k = min(peso / distancia). Saltos: peso mínimo del grafo.",
    )


class ComplejidadTemporal(BaseModel):
    notacion: str = Field(..., description="O(b^m) en la voraz, O(b^d) en A*.")
    b: int = Field(..., description="Factor de ramificación máximo.")
    profundidad: int = Field(
        ..., description="m (voraz): profundidad máxima del espacio; d (A*): de la solución."
    )
    cota: int = Field(..., description="b^profundidad.")
    nodos_generados: int = Field(..., description="Inserciones en la frontera.")
    tiempo_ms: float = Field(..., description="Tiempo medido del ciclo de búsqueda.")


class ComplejidadEspacial(BaseModel):
    notacion: str
    b: int
    profundidad: int
    cota: int
    max_frontera: int = Field(..., description="Mayor tamaño que alcanzó la frontera.")
    max_nodos_en_memoria: int = Field(
        ..., description="Mayor número de nodos guardados a la vez (frontera + explorados)."
    )


class PasoTraza(BaseModel):
    nodo: str
    g: float
    h: float | None = Field(..., description="null = ∞: desde ese nodo no se llega al destino.")
    f: float | None


class BusquedaResponse(BaseModel):
    algoritmo: str
    criterio: str
    heuristica: Heuristica
    origen: str
    destino: str
    limite_nodos: int
    nodos_visitados: int = Field(..., description="No. total de nodos visitados (expandidos).")
    solucion: bool
    ruta: list[str] = Field(..., description="Ruta de solución; vacía si no se encontró.")
    costo: float | None
    motivo: str
    T_n: ComplejidadTemporal = Field(..., alias="T(n)")
    S_n: ComplejidadEspacial = Field(..., alias="S(n)")
    traza: list[PasoTraza] = Field(..., description="Nodos en el orden en que se visitaron.")
    explicacion: str = Field(..., description="Proceso y base teórica del resultado.")


# ---------------------------------------------------------------------------
# Actividad 13: Dijkstra, TSP y generador de grafos
# ---------------------------------------------------------------------------


class DijkstraRequest(GrafoRequest):
    origen: str = Field(..., description="Nodo de inicio.")
    destino: str = Field(..., description="Nodo a alcanzar.")

    @model_validator(mode="after")
    def validar_extremos(self) -> "DijkstraRequest":
        self._validar_nodo("origen")
        self._validar_nodo("destino")
        return self


class TSPRequest(GrafoRequest):
    origen: str | None = Field(
        None,
        description="Nodo donde empieza y termina el ciclo. Por defecto, el primer nodo "
        "del grafo.",
    )

    @model_validator(mode="after")
    def validar_origen(self) -> "TSPRequest":
        if self.origen is None:
            self.origen = next(iter(self.grafo))
        self._validar_nodo("origen")
        return self


class TSPExactoRequest(TSPRequest):
    @model_validator(mode="after")
    def validar_tamano(self) -> "TSPExactoRequest":
        n = len(self.grafo)
        if n > tsp.MAX_NODOS_EXACTO:
            raise ValueError(
                f"El TSP exacto admite hasta {tsp.MAX_NODOS_EXACTO} nodos y el grafo tiene "
                f"{n}: su costo es O(n² · 2ⁿ). Usa /graph/tsp/greedy para grafos grandes."
            )
        return self


class AlgoritmoResponse(BaseModel):
    algoritmo: str
    clase: str = Field(..., description="P, NP-difícil o heurística.")
    complejidad: str = Field(..., description="Complejidad teórica del algoritmo.")
    origen: str
    destino: str | None = Field(
        ...,
        description="null en el TSP (el ciclo regresa al origen) y en BFS/DFS sin destino "
        "(alcance máximo).",
    )
    num_nodos: int = Field(..., description="Nodos del grafo.")
    solucion: bool
    ruta: list[str] = Field(..., description="Camino o ciclo encontrado; vacío si no hay.")
    costo: float | None = Field(..., description="Costo del camino encontrado.")
    nodos_recorridos: int = Field(
        ...,
        description="Dijkstra: nodos fijados. TSP exacto: estados (S, j) evaluados. "
        "TSP voraz: nodos visitados por el agente. BFS/DFS: nodos visitados. "
        "Hill-Climbing: nodos de la ruta recorrida.",
    )
    operaciones: int = Field(
        ...,
        description="Dijkstra: relajaciones. TSP exacto: transiciones evaluadas. "
        "TSP voraz, BFS y DFS: aristas examinadas. Hill-Climbing: vecinos examinados.",
    )
    orden_visita: list[str] | None = Field(
        None, description="BFS, DFS y Hill-Climbing: nodos en el orden en que se visitaron."
    )
    alcance: dict[str, int] | None = Field(
        None,
        description="BFS/DFS sin destino: cada nodo alcanzable con su nivel (BFS: saltos "
        "mínimos) o su profundidad en el árbol DFS.",
    )
    tiempo_ms: float = Field(..., description="Tiempo de ejecución del algoritmo (ms).")
    memoria_kb: float = Field(
        ..., description="Pico de memoria reservada durante la ejecución (KB, tracemalloc)."
    )
    motivo: str
    explicacion: str = Field(..., description="Proceso y base teórica del resultado.")


class GenerarRequest(BaseModel):
    n: int = Field(..., ge=1, le=702, description="Número de nodos (A, B, ..., ZZ).")
    densidad: float = Field(
        0.5,
        ge=0,
        le=1,
        description="Probabilidad de arista entre cada par de nodos además del ciclo base; "
        "1 = grafo completo.",
    )
    peso_min: int = Field(1, ge=1, description="Peso mínimo (pesos aleatorios).")
    peso_max: int = Field(100, ge=1, description="Peso máximo (pesos aleatorios).")
    pesos: Literal["aleatorios", "euclidianos"] = Field(
        "aleatorios",
        description="`aleatorios`: entero en [peso_min, peso_max]. `euclidianos`: distancia "
        "redondeada entre las coordenadas de los extremos.",
    )
    dirigido: bool = False
    semilla: int | None = Field(None, description="Misma semilla, mismo grafo.")

    @model_validator(mode="after")
    def validar_pesos(self) -> "GenerarRequest":
        if self.peso_min > self.peso_max:
            raise ValueError("peso_min no puede ser mayor que peso_max.")
        return self


class GrafoGenerado(BaseModel):
    n: int
    num_aristas: int
    densidad_real: float = Field(..., description="Aristas / aristas posibles.")
    dirigido: bool
    semilla: int | None
    lista_adyacencia: dict[str, list[tuple[str, int]]]
    coordenadas: dict[str, tuple[int, int]]
    explicacion: str


# ---------------------------------------------------------------------------
# Reto integrador, módulo 2: BFS, DFS, Hill-Climbing y comparación
# ---------------------------------------------------------------------------


class RecorridoRequest(GrafoRequest):
    origen: str = Field(..., description="Nodo de inicio.")
    destino: str | None = Field(
        None,
        description="Nodo a alcanzar. Sin destino se calcula el alcance máximo: todos los "
        "nodos alcanzables desde el origen.",
    )

    @model_validator(mode="after")
    def validar_extremos(self) -> "RecorridoRequest":
        self._validar_nodo("origen")
        if self.destino is not None:
            self._validar_nodo("destino")
        return self


AlgoritmoRuta = Literal["bfs", "dfs", "hill-climbing", "greedy", "astar", "dijkstra"]


class CompararRequest(ConHeuristicaRequest):
    destino: str | None = Field(
        None,
        description="Nodo a alcanzar. Sin destino solo se pueden comparar `bfs` y `dfs` "
        "(alcance máximo).",
    )
    algoritmos: list[AlgoritmoRuta] = Field(
        ...,
        min_length=1,
        description="Algoritmos a ejecutar con el mismo grafo.",
    )

    @model_validator(mode="after")
    def validar_algoritmos(self) -> "CompararRequest":
        if len(set(self.algoritmos)) != len(self.algoritmos):
            raise ValueError("La lista `algoritmos` tiene elementos repetidos.")
        if self.destino is None:
            requieren = [a for a in self.algoritmos if a in comparador.REQUIEREN_DESTINO]
            if requieren:
                raise ValueError(
                    f"{', '.join(requieren)} necesita(n) un `destino`; sin destino solo se "
                    "comparan bfs y dfs."
                )
        return self


class FilaComparacion(BaseModel):
    clave: str
    algoritmo: str
    clase: str
    complejidad: str
    solucion: bool
    ruta: list[str]
    costo: float | None
    nodos_recorridos: int
    operaciones: int
    orden_visita: list[str]
    tiempo_ms: float
    memoria_kb: float
    motivo: str


class CompararResponse(BaseModel):
    origen: str
    destino: str | None
    num_nodos: int
    heuristica: Heuristica | None = Field(
        ..., description="Solo si se comparó algún algoritmo que usa h(n)."
    )
    tabla: list[FilaComparacion]
    mejor: str | None = Field(..., description="Algoritmo con la ruta de menor costo.")
    mas_rapido: str
    explicacion: str


# ---------------------------------------------------------------------------
# Reto integrador, módulo 3: benchmark de ordenamiento
# ---------------------------------------------------------------------------

AlgoritmoOrden = Literal[
    "burbuja", "seleccion", "insercion", "merge", "quick", "heap", "counting", "permutaciones"
]
Distribucion = Literal["aleatoria", "ordenada", "inversa", "casi_ordenada"]


def _validar_catalogo(algoritmos: list[str]) -> None:
    if len(set(algoritmos)) != len(algoritmos):
        raise ValueError("La lista `algoritmos` tiene elementos repetidos.")


class OrdenamientoRequest(BaseModel):
    algoritmos: list[AlgoritmoOrden] = Field(
        ..., min_length=2, description="Al menos 2 algoritmos del catálogo."
    )
    datos: list[int | float] | None = Field(
        None,
        max_length=ordenamiento.MAX_N,
        description="Lista a ordenar. Si no se envía, se genera con `n`, `distribucion` "
        "y `semilla`.",
    )
    n: int | None = Field(
        None, ge=1, le=ordenamiento.MAX_N, description="Tamaño de la lista generada."
    )
    distribucion: Distribucion = Field(
        "aleatoria",
        description="Orden de la lista generada: aleatoria (caso promedio), ordenada "
        "(mejor caso), inversa (peor caso) o casi_ordenada.",
    )
    semilla: int | None = Field(None, description="Misma semilla, misma lista.")

    _personalizada: bool = PrivateAttr(default=True)

    @property
    def origen_datos(self) -> str:
        """`personalizada` si el usuario envió la lista; si no, su distribución."""
        return "personalizada" if self._personalizada else self.distribucion

    @model_validator(mode="after")
    def validar_datos(self) -> "OrdenamientoRequest":
        _validar_catalogo(self.algoritmos)
        if self.datos is None:
            self._personalizada = False
            if self.n is None:
                raise ValueError("Envía `datos` (la lista a ordenar) o `n` para generarla.")
            self.datos = generador.generar_lista(self.n, self.distribucion, self.semilla)
        ordenamiento.validar(self.algoritmos, self.datos)
        return self


class ResultadoOrden(BaseModel):
    clave: str
    algoritmo: str
    complejidad: dict[str, str] = Field(..., description="Mejor, promedio y peor caso.")
    espacio: str
    estable: bool
    clase: str
    tiempo_ms: float
    memoria_kb: float = Field(..., description="Pico de memoria reservada (tracemalloc).")
    comparaciones: int
    intercambios: int = Field(
        ...,
        description="Intercambios o escrituras. En permutaciones: permutaciones probadas.",
    )
    correcto: bool = Field(..., description="La salida coincide con sorted().")
    explicacion: str


class OrdenamientoResponse(BaseModel):
    n: int
    distribucion: str = Field(..., description="`personalizada` si se enviaron `datos`.")
    datos_entrada: list[int | float]
    datos_ordenados: list[int | float]
    resultados: list[ResultadoOrden]
    ranking: list[str] = Field(..., description="Claves del más rápido al más lento.")
    explicacion: str


class EscalabilidadRequest(BaseModel):
    algoritmos: list[AlgoritmoOrden] = Field(
        ..., min_length=2, description="Al menos 2 algoritmos del catálogo."
    )
    tamanos: list[int] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Tamaños n a medir (cada uno entre 1 y 50 000).",
    )
    distribucion: Distribucion = "aleatoria"
    semilla: int | None = 0

    @model_validator(mode="after")
    def validar_tamanos(self) -> "EscalabilidadRequest":
        _validar_catalogo(self.algoritmos)
        if any(not 1 <= n <= ordenamiento.MAX_N for n in self.tamanos):
            raise ValueError(f"Cada tamaño debe estar entre 1 y {ordenamiento.MAX_N}.")
        self.tamanos = sorted(set(self.tamanos))
        for clave in self.algoritmos:
            info = ordenamiento.CATALOGO[clave]
            if max(self.tamanos) > info["max_n"]:
                raise ValueError(
                    f"{info['nombre']} admite hasta {info['max_n']} elementos: su costo es "
                    f"{info['peor']}."
                )
        return self


class PuntoSerie(BaseModel):
    n: int
    tiempo_ms: float
    memoria_kb: float
    comparaciones: int


class EscalabilidadResponse(BaseModel):
    distribucion: str
    tamanos: list[int]
    algoritmos: list[dict] = Field(..., description="Metadatos teóricos de cada algoritmo.")
    series: dict[str, list[PuntoSerie]] = Field(
        ..., description="Por algoritmo, un punto por tamaño: listo para graficar."
    )
    explicacion: str


# ---------------------------------------------------------------------------
# Ejemplos para Swagger (/docs), con el grafo de 10 nodos de la actividad
# ---------------------------------------------------------------------------

_GRAFO_10 = {
    "A": [["B", 15], ["C", 22], ["D", 10]],
    "B": [["E", 35], ["F", 18]],
    "C": [["E", 20], ["G", 45]],
    "D": [["F", 28], ["G", 30]],
    "E": [["H", 12], ["I", 25]],
    "F": [["H", 40], ["I", 15]],
    "G": [["I", 10], ["J", 50]],
    "H": [["J", 14]],
    "I": [["J", 8]],
    "J": [],
}

_COORDENADAS_10 = {
    "A": [1521, 193], "B": [1670, 546], "C": [566, 311], "D": [1814, 363], "E": [278, 801],
    "F": [1526, 986], "G": [1399, 1118], "H": [185, 1100], "I": [1032, 1225], "J": [721, 1295],
}

_NODOS_10 = list(_GRAFO_10)

EJEMPLOS = {
    "saltos": Example(
        summary="Grafo de 10 nodos, heurística por saltos",
        value={"lista_adyacencia": _GRAFO_10, "origen": "A", "destino": "J"},
    ),
    "euclidiana": Example(
        summary="Grafo de 10 nodos, heurística euclidiana",
        value={
            "lista_adyacencia": _GRAFO_10,
            "coordenadas": _COORDENADAS_10,
            "origen": "A",
            "destino": "J",
        },
    ),
    "matriz": Example(
        summary="Grafo de 10 nodos como matriz de adyacencia",
        value={
            "nodos": _NODOS_10,
            "matriz_adyacencia": [
                [dict(_GRAFO_10[u]).get(v, 0) for v in _NODOS_10] for u in _NODOS_10
            ],
            "origen": "A",
            "destino": "J",
        },
    ),
    "aristas": Example(
        summary="Vector de aristas con límite de nodos",
        value={
            "aristas": [[u, v, w] for u, vecinos in _GRAFO_10.items() for v, w in vecinos],
            "origen": "A",
            "destino": "J",
            "limite_nodos": 3,
        },
    ),
}


# Grafo de 5 nodos de las pruebas de la Actividad 13 (POST /graph/generate con
# n=5, densidad=0.7, semilla=5): sin dirección, cada arista aparece una vez.
_GRAFO_5 = {
    "A": [["B", 94], ["C", 28], ["D", 53]],
    "B": [["C", 36], ["D", 24], ["E", 99]],
    "C": [["D", 50], ["E", 21]],
    "D": [["E", 98]],
    "E": [],
}

EJEMPLOS_DIJKSTRA = {
    "grafo-5": Example(
        summary="Grafo de 5 nodos, A → E",
        value={"lista_adyacencia": _GRAFO_5, "dirigido": False, "origen": "A", "destino": "E"},
    ),
    "aristas": Example(
        summary="Vector de aristas dirigido",
        value={
            "aristas": [["A", "B", 4], ["A", "C", 1], ["C", "B", 2], ["B", "D", 5]],
            "origen": "A",
            "destino": "D",
        },
    ),
}

EJEMPLOS_TSP = {
    "grafo-5": Example(
        summary="Grafo de 5 nodos, ciclo desde A",
        value={"lista_adyacencia": _GRAFO_5, "dirigido": False, "origen": "A"},
    ),
}

EJEMPLOS_GENERAR = {
    "grafo-10": Example(
        summary="10 nodos, densidad 0.7 (el de las pruebas)",
        value={"n": 10, "densidad": 0.7, "semilla": 7},
    ),
    "completo-euclidiano": Example(
        summary="Grafo completo con pesos euclidianos",
        value={"n": 8, "densidad": 1, "pesos": "euclidianos", "semilla": 1},
    ),
}

EJEMPLOS_RECORRIDO = {
    "ruta": Example(
        summary="Grafo de 5 nodos, A → E",
        value={"lista_adyacencia": _GRAFO_5, "dirigido": False, "origen": "A", "destino": "E"},
    ),
    "alcance": Example(
        summary="Alcance máximo desde A (sin destino)",
        value={"lista_adyacencia": _GRAFO_10, "origen": "A"},
    ),
}

EJEMPLOS_HILL = {
    "saltos": Example(
        summary="Grafo de 10 nodos, heurística por saltos",
        value={"lista_adyacencia": _GRAFO_10, "origen": "A", "destino": "J"},
    ),
    "euclidiana": Example(
        summary="Grafo de 10 nodos, heurística euclidiana",
        value={
            "lista_adyacencia": _GRAFO_10,
            "coordenadas": _COORDENADAS_10,
            "origen": "A",
            "destino": "J",
        },
    ),
}

EJEMPLOS_COMPARAR = {
    "todos": Example(
        summary="Los 6 algoritmos sobre el grafo de 10 nodos",
        value={
            "lista_adyacencia": _GRAFO_10,
            "coordenadas": _COORDENADAS_10,
            "origen": "A",
            "destino": "J",
            "algoritmos": ["bfs", "dfs", "hill-climbing", "greedy", "astar", "dijkstra"],
        },
    ),
    "alcance": Example(
        summary="Alcance máximo con BFS y DFS",
        value={"lista_adyacencia": _GRAFO_10, "origen": "A", "algoritmos": ["bfs", "dfs"]},
    ),
}

EJEMPLOS_ORDENAMIENTO = {
    "generada": Example(
        summary="1000 elementos aleatorios, 4 algoritmos",
        value={
            "algoritmos": ["burbuja", "insercion", "merge", "quick"],
            "n": 1000,
            "distribucion": "aleatoria",
            "semilla": 1,
        },
    ),
    "propia": Example(
        summary="Lista propia, todo el catálogo",
        value={
            "algoritmos": [
                "burbuja", "seleccion", "insercion", "merge",
                "quick", "heap", "counting", "permutaciones",
            ],
            "datos": [5, 3, 8, 1, 9, 2, 7, 4],
        },
    ),
}

EJEMPLOS_ESCALABILIDAD = {
    "cuadraticos-vs-nlogn": Example(
        summary="O(n²) contra O(n log n)",
        value={
            "algoritmos": ["burbuja", "insercion", "merge", "quick", "heap"],
            "tamanos": [100, 500, 1000, 2000],
        },
    ),
}
