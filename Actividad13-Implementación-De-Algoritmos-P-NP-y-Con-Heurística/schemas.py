"""Esquemas de entrada y salida (Pydantic) de todos los endpoints.

La entrada acepta el grafo en tres formatos (lista de adyacencia, matriz de
adyacencia o vector de aristas) y se valida por completo antes de llegar a los
algoritmos: si algo no cuadra, FastAPI responde 422 con el motivo.
"""

from typing import Literal

from fastapi.openapi.models import Example
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from core import grafos, tsp


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


class BusquedaRequest(GrafoRequest):
    origen: str = Field(..., description="Nodo de inicio.")
    destino: str = Field(..., description="Nodo a alcanzar.")
    limite_nodos: int | None = Field(
        None,
        ge=1,
        description="Máximo de nodos a visitar (expandir). Por defecto, el 80 % del "
        "número total de nodos, redondeado hacia arriba.",
    )
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
    def validar_busqueda(self) -> "BusquedaRequest":
        grafo = self.grafo
        for campo in ("origen", "destino"):
            self._validar_nodo(campo)

        if self.heuristica is None:
            self.heuristica = "euclidiana" if self.coordenadas else "saltos"
        if self.heuristica == "euclidiana":
            grafos.validar_coordenadas(grafo, self.coordenadas)
        if self.limite_nodos is None:
            self.limite_nodos = grafos.limite_por_defecto(len(grafo))
        return self


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
    destino: str | None = Field(..., description="null en el TSP: el ciclo regresa al origen.")
    num_nodos: int = Field(..., description="Nodos del grafo.")
    solucion: bool
    ruta: list[str] = Field(..., description="Camino o ciclo encontrado; vacío si no hay.")
    costo: float | None = Field(..., description="Costo del camino encontrado.")
    nodos_recorridos: int = Field(
        ...,
        description="Dijkstra: nodos fijados. TSP exacto: estados (S, j) evaluados. "
        "TSP voraz: nodos visitados por el agente.",
    )
    operaciones: int = Field(
        ...,
        description="Dijkstra: relajaciones. TSP exacto: transiciones evaluadas. "
        "TSP voraz: aristas examinadas.",
    )
    tiempo_ms: float = Field(..., description="Tiempo de ejecución del algoritmo (ms).")
    memoria_kb: float = Field(
        ..., description="Pico de memoria reservada durante la ejecución (KB, tracemalloc)."
    )
    motivo: str


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
