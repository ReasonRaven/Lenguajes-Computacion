from fastapi import FastAPI

from routers import afd, afnd, complejidad

app = FastAPI(
    title="Evaluadores de autómatas y analizador de complejidad",
    description="API para la Actividad 11 de Lenguajes Computacionales "
    "(escala el backend de AFD/AFND de la Actividad 6).",
)

app.include_router(afd.router)
app.include_router(afnd.router)
app.include_router(complejidad.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
