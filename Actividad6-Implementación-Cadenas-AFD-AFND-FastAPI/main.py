from fastapi import FastAPI

from routers import afd, afnd

app = FastAPI(
    title="Evaluadores de AFD y AFND",
    description="API para la Actividad 6 de Lenguajes Computacionales",
)

app.include_router(afd.router)
app.include_router(afnd.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
