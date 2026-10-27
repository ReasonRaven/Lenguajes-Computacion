"""Esquemas de entrada y salida (Pydantic) de todos los endpoints.

Los números viajan como **cadenas**: un entero de 100 dígitos no cabe en un
número de JSON sin perder precisión (JavaScript, por ejemplo, solo representa
exactamente enteros de hasta ~16 dígitos). Se validan antes de llegar a los
algoritmos: si algo no cuadra, FastAPI responde 422 con el motivo.
"""

from fastapi.openapi.models import Example
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from core import digitos, karatsuba

MAX_DIGITOS = 5000  # la escolar con 5000 dígitos ya tarda varios segundos


class MultiplicarRequest(BaseModel):
    a: str = Field(..., description="Primer factor, entero en base 10 (admite signo `-`).")
    b: str = Field(..., description="Segundo factor, entero en base 10 (admite signo `-`).")
    repeticiones: int = Field(
        5,
        ge=1,
        le=100,
        description="Veces que se ejecuta el algoritmo para medir el tiempo; se reporta la "
        "mediana.",
    )

    _x: tuple[bool, digitos.Digitos] = PrivateAttr()
    _y: tuple[bool, digitos.Digitos] = PrivateAttr()

    @model_validator(mode="after")
    def validar_numeros(self) -> "MultiplicarRequest":
        self._x = digitos.parsear(self.a)
        self._y = digitos.parsear(self.b)
        if max(len(self._x[1]), len(self._y[1])) > MAX_DIGITOS:
            raise ValueError(f"cada factor puede tener a lo más {MAX_DIGITOS} dígitos")
        return self

    @property
    def x(self) -> tuple[bool, digitos.Digitos]:
        """(es negativo, dígitos little-endian) del primer factor."""
        return self._x

    @property
    def y(self) -> tuple[bool, digitos.Digitos]:
        return self._y


class KaratsubaRequest(MultiplicarRequest):
    umbral: int = Field(
        1,
        ge=1,
        le=MAX_DIGITOS,
        description="Tamaño (en dígitos) a partir del cual se deja de dividir. `1` = Karatsuba "
        f"puro; mayor que 1 = híbrido (usa la escolar en subproblemas de `umbral` dígitos o "
        f"menos; se sugiere {karatsuba.UMBRAL_HIBRIDO}).",
    )


class CompararRequest(MultiplicarRequest):
    umbral: int = Field(
        karatsuba.UMBRAL_HIBRIDO,
        ge=2,
        le=MAX_DIGITOS,
        description="Umbral de la variante híbrida.",
    )


class MultiplicacionResponse(BaseModel):
    algoritmo: str
    complejidad_tiempo: str
    complejidad_espacio: str
    a: str
    b: str
    producto: str
    num_digitos: int = Field(..., description="N: dígitos del factor más largo.")
    digitos_producto: int
    multiplicaciones: int = Field(
        ..., description="Multiplicaciones de un dígito por un dígito que se realizaron."
    )
    llamadas_recursivas: int = Field(..., description="0 en la tradicional.")
    profundidad: int = Field(..., description="Profundidad máxima de la recursión.")
    umbral: int | None = Field(None, description="Umbral de Karatsuba; null en la tradicional.")
    tiempo_ms: float = Field(..., description="T(N): mediana del tiempo de ejecución, en ms.")
    memoria_kb: float = Field(..., description="S(N): pico de memoria reservada, en KB.")


class CompararResponse(BaseModel):
    num_digitos: int
    producto: str
    coinciden: bool = Field(
        ...,
        description="Las tres variantes dieron el mismo producto, y es igual al de la "
        "multiplicación nativa de Python (referencia).",
    )
    resultados: list[MultiplicacionResponse]
    aceleracion_puro: float = Field(
        ..., description="tiempo tradicional / tiempo Karatsuba puro (> 1: Karatsuba gana)."
    )
    aceleracion_hibrido: float = Field(
        ..., description="tiempo tradicional / tiempo Karatsuba híbrido."
    )
    ahorro_multiplicaciones: float = Field(
        ...,
        description="Fracción de multiplicaciones de un dígito que se ahorra Karatsuba puro "
        "respecto a la tradicional.",
    )


class GenerarRequest(BaseModel):
    n: int = Field(..., ge=1, le=MAX_DIGITOS, description="Dígitos de cada número.")
    semilla: int | None = Field(None, description="Semilla para obtener siempre los mismos.")


class NumerosGenerados(BaseModel):
    n: int
    semilla: int | None
    a: str
    b: str


# ---------------------------------------------------------------------------
# Ejemplos para /docs: los números de 20, 50 y 100 dígitos de las pruebas
# ---------------------------------------------------------------------------

_N20 = ("53125464378932587713", "65438219987021445523")
_N50 = (
    "48390057284612398740021394857739210034875610293847",
    "91827364550019283746501928374655019283746550192837",
)
_N100 = (
    "3141592653589793238462643383279502884197169399375105820974944592"
    "307816406286208998628034825342117067",
    "2718281828459045235360287471352662497757247093699959574966967627"
    "724076630353547594571382178525166427",
)


def _ejemplos(extra: dict | None = None) -> dict[str, Example]:
    extra = extra or {}
    return {
        "20-digitos": Example(summary="20 dígitos", value={"a": _N20[0], "b": _N20[1], **extra}),
        "50-digitos": Example(summary="50 dígitos", value={"a": _N50[0], "b": _N50[1], **extra}),
        "100-digitos": Example(
            summary="100 dígitos (π y e)", value={"a": _N100[0], "b": _N100[1], **extra}
        ),
        "ejemplo-a-mano": Example(
            summary="1234 × 5678 (ejemplo del README)", value={"a": "1234", "b": "5678", **extra}
        ),
    }


EJEMPLOS_TRADICIONAL = _ejemplos()
EJEMPLOS_KARATSUBA = {
    **_ejemplos({"umbral": 1}),
    "hibrido": Example(
        summary="100 dígitos, híbrido con umbral 16",
        value={"a": _N100[0], "b": _N100[1], "umbral": karatsuba.UMBRAL_HIBRIDO},
    ),
}
EJEMPLOS_COMPARAR = _ejemplos()
EJEMPLOS_GENERAR = {
    str(n): Example(summary=f"{n} dígitos", value={"n": n, "semilla": n}) for n in (20, 50, 100)
}
