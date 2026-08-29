from fastapi import FastAPI

from routers import cadenas, lenguajes

app = FastAPI(
    title="Operaciones con cadenas y lenguajes",
    description="API para la Actividad 3 de Lenguajes Computacionales",
)

app.include_router(cadenas.router)
app.include_router(lenguajes.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
