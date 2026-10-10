"""Esquemas de entrada y salida (Pydantic) de los endpoints de búsqueda.

La entrada acepta el grafo en tres formatos (lista de adyacencia, matriz de
adyacencia o vector de aristas) y se valida por completo antes de llegar a los
algoritmos: si algo no cuadra, FastAPI responde 422 con el motivo.
"""

from typing import Literal

from fastapi.openapi.models import Example
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from core import grafos


class BusquedaRequest(BaseModel):
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
    dirigido: bool = Field(
        True, description="Con `false` cada arista se recorre en ambos sentidos."
    )

    _grafo: grafos.Grafo = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def validar(self) -> "BusquedaRequest":
        grafo = grafos.construir_grafo(
            self.lista_adyacencia,
            self.matriz_adyacencia,
            self.nodos,
            self.aristas,
            self.dirigido,
        )
        for campo in ("origen", "destino"):
            nodo = getattr(self, campo)
            if nodo not in grafo:
                raise ValueError(f"El {campo} '{nodo}' no es un nodo del grafo.")

        if self.heuristica is None:
            self.heuristica = "euclidiana" if self.coordenadas else "saltos"
        if self.heuristica == "euclidiana":
            grafos.validar_coordenadas(grafo, self.coordenadas)
        if self.limite_nodos is None:
            self.limite_nodos = grafos.limite_por_defecto(len(grafo))

        self._grafo = grafo
        return self

    @property
    def grafo(self) -> grafos.Grafo:
        """El grafo ya normalizado a lista de adyacencia."""
        return self._grafo


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
