from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core import afnd as afnd_ops
from core.automatas import AutomataInvalido

router = APIRouter(prefix="/afnd", tags=["AFND"])


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


@router.post("/evaluar")
def evaluar(body: EvaluarAFNDRequest) -> dict:
    try:
        return afnd_ops.evaluar(
            body.tabla, body.estado_inicial, body.estados_finales, body.cadenas
        )
    except AutomataInvalido as error:
        raise HTTPException(status_code=422, detail=str(error))
