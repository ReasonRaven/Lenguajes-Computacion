from typing import Annotated

from fastapi import APIRouter, Body

from core import explicaciones, generador, metricas, ordenamiento
from schemas import (
    EJEMPLOS_ESCALABILIDAD,
    EJEMPLOS_ORDENAMIENTO,
    EscalabilidadRequest,
    EscalabilidadResponse,
    OrdenamientoRequest,
    OrdenamientoResponse,
)

router = APIRouter(prefix="/benchmark", tags=["Módulo 3 · Escalabilidad y benchmark"])

_RESPUESTAS = {
    422: {
        "description": "Entrada inválida: menos de 2 algoritmos, lista demasiado grande "
        "para un algoritmo (p. ej. permutaciones con más de 8 elementos) o counting sort "
        "con valores no enteros."
    }
}


@router.post(
    "/ordenamiento",
    summary="Comparar algoritmos de ordenamiento con los mismos datos",
    response_model=OrdenamientoResponse,
    responses=_RESPUESTAS,
)
def comparar_ordenamiento(
    body: Annotated[OrdenamientoRequest, Body(openapi_examples=EJEMPLOS_ORDENAMIENTO)],
) -> dict:
    """Ordena la misma lista con cada algoritmo elegido y reporta tiempo, memoria,
    comparaciones e intercambios, junto con su complejidad teórica y su clase."""
    esperado = sorted(body.datos)
    resultados = []
    for clave in body.algoritmos:
        info = ordenamiento.CATALOGO[clave]
        (ordenada, comparaciones, intercambios), tiempo_ms, memoria_kb = metricas.medir(
            info["funcion"], body.datos
        )
        resultados.append(
            {
                **ordenamiento.metadatos(clave),
                "tiempo_ms": tiempo_ms,
                "memoria_kb": memoria_kb,
                "comparaciones": comparaciones,
                "intercambios": intercambios,
                "correcto": ordenada == esperado,
                "explicacion": info["idea"],
            }
        )

    ranking = [r["clave"] for r in sorted(resultados, key=lambda r: r["tiempo_ms"])]
    general, por_algoritmo = explicaciones.ordenamiento(
        len(body.datos), body.origen_datos, resultados, ranking
    )
    for r, explicacion in zip(resultados, por_algoritmo):
        r["explicacion"] = explicacion
    return {
        "n": len(body.datos),
        "distribucion": body.origen_datos,
        "datos_entrada": body.datos,
        "datos_ordenados": esperado,
        "resultados": resultados,
        "ranking": ranking,
        **general,
    }


@router.post(
    "/escalabilidad",
    summary="Medir cómo crece el tiempo de cada algoritmo con n",
    response_model=EscalabilidadResponse,
    responses=_RESPUESTAS,
)
def escalabilidad(
    body: Annotated[EscalabilidadRequest, Body(openapi_examples=EJEMPLOS_ESCALABILIDAD)],
) -> dict:
    """Ejecuta cada algoritmo con listas de cada tamaño de `tamanos` (las mismas para
    todos) y devuelve una serie por algoritmo, lista para la gráfica comparativa."""
    listas = {n: generador.generar_lista(n, body.distribucion, body.semilla) for n in body.tamanos}
    series: dict[str, list[dict]] = {}
    for clave in body.algoritmos:
        funcion = ordenamiento.CATALOGO[clave]["funcion"]
        series[clave] = []
        for n, datos in listas.items():
            (_, comparaciones, _), tiempo_ms, memoria_kb = metricas.medir(funcion, datos)
            series[clave].append(
                {
                    "n": n,
                    "tiempo_ms": tiempo_ms,
                    "memoria_kb": memoria_kb,
                    "comparaciones": comparaciones,
                }
            )

    nombres = {clave: ordenamiento.CATALOGO[clave]["nombre"] for clave in body.algoritmos}
    return {
        "distribucion": body.distribucion,
        "tamanos": body.tamanos,
        "algoritmos": [ordenamiento.metadatos(clave) for clave in body.algoritmos],
        "series": series,
        **explicaciones.escalabilidad(series, nombres, body.distribucion),
    }
