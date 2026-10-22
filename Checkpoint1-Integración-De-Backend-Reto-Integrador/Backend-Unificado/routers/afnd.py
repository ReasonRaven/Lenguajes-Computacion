from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core import afnd as afnd_ops
from core import explicaciones
from core.automatas import AutomataInvalido

router = APIRouter(prefix="/afnd", tags=["Módulo 1 · Lenguajes y autómatas"])
# El mismo evaluador bajo /afnd-e: un AFND con transiciones λ (ε) es un AFND-ε.
router_e = APIRouter(prefix="/afnd-e", tags=["Módulo 1 · Lenguajes y autómatas"])


class EvaluarAFNDRequest(BaseModel):
    tabla: dict[str, dict[str, str | list[str] | None]] = Field(
        ...,
        description=(
            "Tabla de transición: estado -> símbolo -> lista de estados destino. "
            "La columna λ (también 'lambda', 'ε' o '') es opcional y no forma "
            "parte del alfabeto."
        ),
        examples=[
            {
                "q0": {"a": ["q0", "q1"], "b": ["q0"]},
                "q1": {"b": ["q2"]},
                "q2": {"b": ["q3"]},
                "q3": {},
            }
        ],
    )
    estado_inicial: str = Field(..., examples=["q0"])
    estados_finales: list[str] = Field(..., examples=[["q3"]])
    cadenas: list[str] = Field(..., examples=[["abb", "aabb", "ab"]])


@router.post("/evaluar", summary="Evaluar cadenas en un AFND (con o sin λ)")
@router_e.post("/evaluar", summary="Evaluar cadenas en un AFND-ε (con transiciones λ/ε)")
def evaluar(body: EvaluarAFNDRequest) -> dict:
    try:
        resultado = afnd_ops.evaluar(
            body.tabla, body.estado_inicial, body.estados_finales, body.cadenas
        )
    except AutomataInvalido as error:
        raise HTTPException(status_code=422, detail=str(error))
    general, por_cadena = explicaciones.automata(
        resultado["tipo"], body.estado_inicial, body.estados_finales, resultado["resultados"]
    )
    for r, explicacion in zip(resultado["resultados"], por_cadena):
        r["explicacion"] = explicacion
    return {**resultado, **general}
