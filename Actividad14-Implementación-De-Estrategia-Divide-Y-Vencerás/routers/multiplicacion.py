from typing import Annotated, Callable

from fastapi import APIRouter, Body

from core import digitos, generador, karatsuba, metricas, tradicional
from schemas import (
    EJEMPLOS_COMPARAR,
    EJEMPLOS_GENERAR,
    EJEMPLOS_KARATSUBA,
    EJEMPLOS_TRADICIONAL,
    CompararRequest,
    CompararResponse,
    GenerarRequest,
    KaratsubaRequest,
    MultiplicacionResponse,
    MultiplicarRequest,
    NumerosGenerados,
)

router = APIRouter(prefix="/multiply", tags=["Multiplicación de enteros grandes"])

_RESPUESTAS = {
    422: {
        "description": "Entrada inválida: algún factor no es un entero en base 10 o "
        "tiene demasiados dígitos."
    }
}


def _ejecutar(
    info: dict, algoritmo: Callable[..., dict], body: MultiplicarRequest, *extra: int
) -> dict:
    (neg_x, x), (neg_y, y) = body.x, body.y
    resultado, tiempo_ms, memoria_kb = metricas.medir(
        algoritmo, x, y, *extra, repeticiones=body.repeticiones
    )
    producto = digitos.formatear(neg_x != neg_y, resultado.pop("digitos"))
    return {
        **info,
        **resultado,
        "a": body.a,
        "b": body.b,
        "producto": producto,
        "num_digitos": max(len(x), len(y)),
        "digitos_producto": len(producto.lstrip("-")),
        "tiempo_ms": tiempo_ms,
        "memoria_kb": memoria_kb,
    }


def _tradicional(body: MultiplicarRequest) -> dict:
    info = {
        "algoritmo": tradicional.ALGORITMO,
        "complejidad_tiempo": tradicional.COMPLEJIDAD_TIEMPO,
        "complejidad_espacio": tradicional.COMPLEJIDAD_ESPACIO,
        "umbral": None,
    }
    return _ejecutar(info, tradicional.tradicional, body)


def _karatsuba(body: MultiplicarRequest, umbral: int) -> dict:
    info = {
        "algoritmo": karatsuba.ALGORITMO_PURO if umbral == 1 else karatsuba.ALGORITMO_HIBRIDO,
        "complejidad_tiempo": karatsuba.COMPLEJIDAD_TIEMPO,
        "complejidad_espacio": karatsuba.COMPLEJIDAD_ESPACIO,
        "umbral": umbral,
    }
    return _ejecutar(info, karatsuba.karatsuba, body, umbral)


@router.post(
    "/tradicional",
    summary="Multiplicación tradicional (sin Karatsuba)",
    response_model=MultiplicacionResponse,
    responses=_RESPUESTAS,
)
def ruta_tradicional(
    body: Annotated[MultiplicarRequest, Body(openapi_examples=EJEMPLOS_TRADICIONAL)],
) -> dict:
    """Multiplicación escolar dígito por dígito: `n · m` multiplicaciones de un dígito,
    `O(n²)`."""
    return _tradicional(body)


@router.post(
    "/karatsuba",
    summary="Karatsuba recursivo (divide y vencerás)",
    response_model=MultiplicacionResponse,
    responses=_RESPUESTAS,
)
def ruta_karatsuba(
    body: Annotated[KaratsubaRequest, Body(openapi_examples=EJEMPLOS_KARATSUBA)],
) -> dict:
    """Karatsuba recursivo: 3 productos de la mitad de tamaño en vez de 4,
    `O(n^1.585)`. Con `umbral = 1` es la versión pura; con `umbral > 1`, la híbrida."""
    return _karatsuba(body, body.umbral)


@router.post(
    "/comparar",
    summary="Compara tradicional, Karatsuba puro y Karatsuba híbrido",
    response_model=CompararResponse,
    responses=_RESPUESTAS,
)
def ruta_comparar(
    body: Annotated[CompararRequest, Body(openapi_examples=EJEMPLOS_COMPARAR)],
) -> dict:
    """Multiplica los mismos factores con las tres variantes, verifica que den el mismo
    producto (y que coincida con la multiplicación nativa de Python) y calcula la
    aceleración de Karatsuba respecto a la tradicional."""
    resultados = [_tradicional(body), _karatsuba(body, 1), _karatsuba(body, body.umbral)]
    trad, puro, hibrido = resultados
    referencia = str(int(body.a) * int(body.b))
    return {
        "num_digitos": trad["num_digitos"],
        "producto": trad["producto"],
        "coinciden": all(r["producto"] == referencia for r in resultados),
        "resultados": resultados,
        "aceleracion_puro": _cociente(trad["tiempo_ms"], puro["tiempo_ms"]),
        "aceleracion_hibrido": _cociente(trad["tiempo_ms"], hibrido["tiempo_ms"]),
        "ahorro_multiplicaciones": round(
            1 - puro["multiplicaciones"] / trad["multiplicaciones"], 4
        ),
    }


def _cociente(a: float, b: float) -> float:
    return round(a / b, 3) if b else 0.0


@router.post("/generate", summary="Genera dos enteros de N dígitos", response_model=NumerosGenerados)
def ruta_generar(body: Annotated[GenerarRequest, Body(openapi_examples=EJEMPLOS_GENERAR)]) -> dict:
    """Dos enteros aleatorios de exactamente `n` dígitos, para usarlos como entrada de los
    demás endpoints."""
    a, b = generador.generar(body.n, body.semilla)
    return {"n": body.n, "semilla": body.semilla, "a": a, "b": b}
