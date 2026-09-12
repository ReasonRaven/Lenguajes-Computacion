# Lenguajes de la Computación

Repositorio de tareas y actividades de la materia **Lenguajes de la Computación**
(5.º semestre).

**Autor:** Jonathan Hernández Lazcano · No. de cuenta 200417

Cada actividad es un proyecto independiente con su propia API en **FastAPI**, un
notebook con el desarrollo de los ejercicios y un `README.md` propio con la teoría,
las peticiones y los resultados.

## Actividades

| # | Actividad | Contenido | Documentación |
|---|---|---|---|
| 3 | Operaciones con cadenas y lenguajes | Concatenación, potencia, unión, intersección, diferencia, complemento y clausura de Kleene | [README](Actividad3-Operaciones-Cadenas-Lenguajes/README.md) |
| 6 | Implementación de AFD y AFND | Evaluadores de autómatas finitos deterministas y no deterministas, con soporte de transiciones λ | [README](Actividad6-Implementación-Cadenas-AFD-AFND-FastAPI/README.md) |

> La Actividad 6 se desarrolló en equipo con Camila Rodriguez Rosas (194100).

## Estructura

Las dos actividades comparten la misma organización:

```
ActividadN-.../
├── main.py            # Punto de entrada de FastAPI: crea la app y monta los routers
├── core/              # Lógica pura (sin dependencias de FastAPI)
├── routers/           # Endpoints HTTP y modelos de petición/respuesta
├── notebooks/
│   └── ejercicios.ipynb   # Desarrollo paso a paso de los ejercicios
├── requirements.txt
└── README.md          # Teoría, endpoints, ejercicios y resultados
```

La separación entre `core/` y `routers/` permite usar la lógica tanto desde la API
como directamente desde el notebook.

## Cómo ejecutar

Los comandos se ejecutan **dentro de la carpeta de la actividad**, no en la raíz.

```bash
cd Actividad3-Operaciones-Cadenas-Lenguajes   # o la actividad que corresponda

python3 -m venv .venv
source .venv/bin/activate                     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Levantar la API (documentación interactiva en http://127.0.0.1:8000/docs)
uvicorn main:app --reload

# Ejecutar el notebook con el desarrollo de los ejercicios
jupyter notebook notebooks/ejercicios.ipynb
```

Con la API levantada, `/docs` ofrece la interfaz de Swagger para probar cada
endpoint sin escribir código.

## Tecnologías

- **Python 3.13+**
- **FastAPI** + **Uvicorn** — API y servidor de desarrollo
- **Pydantic** — validación de las peticiones
- **Jupyter** — notebooks con el desarrollo de los ejercicios
