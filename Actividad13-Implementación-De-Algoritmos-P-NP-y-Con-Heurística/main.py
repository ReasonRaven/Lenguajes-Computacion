from fastapi import FastAPI

from routers import busqueda, grafos

app = FastAPI(
    title="Algoritmos P, NP y con heurística",
    description="API para la Actividad 13 de Lenguajes Computacionales: Dijkstra, problema "
    "del agente viajero (exacto y con heurística voraz) y generador de grafos sintéticos. "
    "Conserva la búsqueda voraz y A* de la Actividad 12.",
)

app.include_router(grafos.router)
app.include_router(busqueda.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
