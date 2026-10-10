from fastapi import FastAPI

from routers import busqueda

app = FastAPI(
    title="Algoritmos de búsqueda informada",
    description="API para la Actividad 12 de Lenguajes Computacionales: búsqueda voraz "
    "(Greedy Best-First) y búsqueda A* sobre grafos ponderados.",
)

app.include_router(busqueda.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
