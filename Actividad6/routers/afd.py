from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core import afd as afd_ops
from core.automatas import AutomataInvalido

router = APIRouter(prefix="/afd", tags=["AFD"])


class EvaluarAFDRequest(BaseModel):
    tabla: dict[str, dict[str, str | list[str] | None]] = Field(
        ...,
        description="Tabla de transición: estado -> símbolo -> estado destino.",
        examples=[{"q0": {"a": "q1", "b": "q0"}, "q1": {"a": "q0", "b": "q1"}}],
    )
    estado_inicial: str = Field(..., examples=["q0"])
    estados_finales: list[str] = Field(..., examples=[["q0"]])
    cadenas: list[str] = Field(..., examples=[["", "aa", "aba"]])


@router.post("/evaluar")
def evaluar(body: EvaluarAFDRequest) -> dict:
    try:
        return afd_ops.evaluar(
            body.tabla, body.estado_inicial, body.estados_finales, body.cadenas
        )
    except AutomataInvalido as error:
        raise HTTPException(status_code=422, detail=str(error))
