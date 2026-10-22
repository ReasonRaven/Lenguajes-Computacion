from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# GEMINI_API_KEY, GEMINI_MODEL y GEMINI_TIMEOUT se leen de Backend-Unificado/.env.
load_dotenv()

from routers import afd, afnd, benchmark, busqueda, cadenas, complejidad, grafos, lenguajes

app = FastAPI(
    title="Reto Integrador (Examen parcial #2): backend",
    description="Backend del producto para experimentar con autómatas, optimización de "
    "rutas y complejidad algorítmica. Reúne las actividades 3, 6, 11, 12 y 13 de Lenguajes "
    "Computacionales y las organiza en tres módulos: (1) traductor de lenguajes y "
    "verificador de reglas, (2) asistente de logística y optimización y (3) auditoría de "
    "escalabilidad y benchmark. Cada respuesta incluye `explicacion`: el proceso y la base "
    "teórica del resultado, generados con un modelo de Google Gemini (o con una plantilla si la IA "
    "no está disponible; lo indica `explicacion_ia`).",
)

# El frontend (Frontend/, React + Vite) puede servirse desde otro origen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Módulo 1: lenguajes y autómatas
app.include_router(cadenas.router)
app.include_router(lenguajes.router)
app.include_router(afd.router)
app.include_router(afnd.router)
app.include_router(afnd.router_e)

# Módulo 2: logística y optimización
app.include_router(grafos.router)
app.include_router(busqueda.router)

# Módulo 3: escalabilidad y benchmark
app.include_router(benchmark.router)
app.include_router(complejidad.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok"}
