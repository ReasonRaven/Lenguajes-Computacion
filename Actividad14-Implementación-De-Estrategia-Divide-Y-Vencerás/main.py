from fastapi import FastAPI

from routers import multiplicacion

app = FastAPI(
    title="Divide y vencerás: Karatsuba",
    description="API para la Actividad 14 de Lenguajes Computacionales: multiplicación de "
    "enteros gigantes con el algoritmo de Karatsuba recursivo (puro e híbrido), comparada "
    "contra la multiplicación tradicional. Cada respuesta incluye el tiempo T(N) y el espacio "
    "S(N) medidos.",
)

app.include_router(multiplicacion.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
