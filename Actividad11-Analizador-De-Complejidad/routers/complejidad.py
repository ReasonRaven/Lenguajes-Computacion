from enum import Enum

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse

from core import complejidad as complejidad_ops

router = APIRouter(prefix="/complejidad", tags=["Complejidad"])


class Formato(str, Enum):
    archivo = "archivo"
    json = "json"


_RESPUESTAS = {
    200: {
        "description": "Archivo anotado (`formato=archivo`) o análisis en JSON (`formato=json`).",
        "content": {"text/x-python": {}},
    },
    422: {"description": "El archivo no es UTF-8 o no es un programa de Python válido."},
}

_DESCRIPCION_ARCHIVO = "Programa en Python a analizar (.py)."
_DESCRIPCION_FORMATO = (
    "`archivo`: devuelve el programa con la complejidad comentada línea por línea y un "
    "bloque final de resumen. `json`: devuelve el análisis estructurado."
)


async def _analizar(archivo: UploadFile, caso: str, formato: Formato):
    contenido = await archivo.read()
    try:
        codigo = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="El archivo debe estar codificado en UTF-8.")

    nombre = archivo.filename or "programa.py"
    try:
        resultado = complejidad_ops.analizar(codigo, caso, nombre)
    except complejidad_ops.ProgramaInvalido as error:
        raise HTTPException(status_code=422, detail=str(error))

    if formato is Formato.json:
        return resultado
    return PlainTextResponse(
        resultado["archivo_anotado"],
        media_type="text/x-python; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{complejidad_ops.nombre_salida(nombre, caso)}"'
            )
        },
    )


@router.post("/peor-caso", summary="Complejidad en el peor caso (Big-O)", responses=_RESPUESTAS)
async def peor_caso(
    archivo: UploadFile = File(..., description=_DESCRIPCION_ARCHIVO),
    formato: Formato = Query(Formato.archivo, description=_DESCRIPCION_FORMATO),
):
    """Analiza el programa tomando siempre el camino más costoso y anota cada línea
    con su complejidad en notación **Big-O**."""
    return await _analizar(archivo, complejidad_ops.PEOR, formato)


@router.post("/mejor-caso", summary="Complejidad en el mejor caso (Big-Ω)", responses=_RESPUESTAS)
async def mejor_caso(
    archivo: UploadFile = File(..., description=_DESCRIPCION_ARCHIVO),
    formato: Formato = Query(Formato.archivo, description=_DESCRIPCION_FORMATO),
):
    """Analiza el programa tomando el camino más barato (salidas tempranas de los
    ciclos, rama más económica de cada `if`) y anota cada línea con su complejidad
    en notación **Big-Omega (Ω)**."""
    return await _analizar(archivo, complejidad_ops.MEJOR, formato)
