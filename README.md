# Lenguajes de la Computación

Repositorio de tareas y actividades de la materia **Lenguajes de la Computación**
(5.º semestre).

**Autor:** Jonathan Hernández Lazcano · No. de cuenta 200417

Cada actividad es un proyecto independiente con su propia API en **FastAPI** y un
`README.md` propio con la teoría, las peticiones y los resultados. Las actividades 3 y 6
incluyen además un notebook con el desarrollo de los ejercicios.

## Actividades

| # | Actividad | Contenido | Documentación |
|---|---|---|---|
| 3 | Operaciones con cadenas y lenguajes | Concatenación, potencia, unión, intersección, diferencia, complemento y clausura de Kleene | [README](Actividad3-Operaciones-Cadenas-Lenguajes/README.md) |
| 6 | Implementación de AFD y AFND | Evaluadores de autómatas finitos deterministas y no deterministas, con soporte de transiciones λ | [README](Actividad6-Implementación-Cadenas-AFD-AFND-FastAPI/README.md) |
| 11 | Analizador de complejidad | Escala el backend de la Actividad 6 con un analizador que anota la complejidad Big-O / Big-Ω de un programa línea por línea | [README](Actividad11-Analizador-De-Complejidad/README.md) |
| 12 | Algoritmos de búsqueda informada | Búsqueda voraz (Greedy Best-First) y A* sobre grafos ponderados, con heurística euclidiana o por saltos | [README](Actividad12-Algoritmos-De-Búsqueda-Informada-Heurísticos/README.md) |
| 13 | Algoritmos P, NP y con heurística | Continúa el backend de la Actividad 12 con Dijkstra, el agente viajero exacto (Held-Karp) y con heurística voraz, y un generador de grafos sintéticos; reporta tiempo, memoria, nodos recorridos y costo | [README](Actividad13-Implementación-De-Algoritmos-P-NP-y-Con-Heurística/README.md) |
| 14 | Divide y vencerás: Karatsuba | Multiplicación de enteros gigantes con Karatsuba recursivo (puro e híbrido) sobre listas de dígitos, comparada contra la multiplicación tradicional; mide T(N) y S(N) con 20, 50, 100 y hasta 2 000 dígitos | [README](Actividad14-Implementación-De-Estrategia-Divide-Y-Vencerás/README.md) |
| Checkpoint 1 | Integración de backend: Reto Integrador (Examen parcial #2) | Aplicación web (FastAPI + React) que reúne las actividades 3, 6, 11, 12 y 13 en tres módulos: lenguajes y autómatas, logística y optimización, y benchmark | [README](Checkpoint1-Integración-De-Backend-Reto-Integrador/README.md) |

> Las actividades 6, 11, 12, 13 y 14 se desarrollaron en equipo con Camila Rodriguez Rosas (194100).

### Reto Integrador (Examen parcial #2)

Aplicación web para experimentar con autómatas, rutas y complejidad algorítmica, en
[`Checkpoint1-Integración-De-Backend-Reto-Integrador/`](Checkpoint1-Integración-De-Backend-Reto-Integrador/README.md):

- [`Backend-Unificado/`](Checkpoint1-Integración-De-Backend-Reto-Integrador/Backend-Unificado/README.md) (FastAPI) reúne en una sola API los
  endpoints de todas las actividades, organizados en tres módulos: lenguajes y autómatas,
  logística y optimización, y benchmark. Agrega BFS, DFS, Hill-Climbing, la comparación de
  algoritmos sobre el mismo grafo, un benchmark de algoritmos de ordenamiento y una
  explicación teórica en cada respuesta.
- [`Frontend/`](Checkpoint1-Integración-De-Backend-Reto-Integrador/Frontend/README.md) (React + Vite) es la interfaz gráfica: formularios,
  editor de autómatas, grafos con la ruta resaltada, tablas comparativas y gráficas.

Para usarla: `uvicorn main:app --reload` en `Backend-Unificado/` y, en otra terminal,
`npm install && npm run dev` en `Frontend/`; luego abrir http://localhost:5173. Las
carpetas de cada actividad siguen siendo proyectos independientes.

Integrantes: Jonathan Hernández Lazcano (200417), Camila Rodriguez Rosas (194100) y
Daniel Peña Cruz (200818).

### Endpoints por actividad

Los endpoints son `POST` y trabajan con JSON, salvo los de complejidad, que reciben un
archivo (`multipart/form-data`) y lo devuelven anotado. Cada API expone además
`GET /` como verificación de estado (`{"status": "ok"}`).

| Actividad | Endpoints |
|---|---|
| 3 | `/cadenas/concatenar`, `/cadenas/unir`, `/cadenas/potencia` |
| 3 | `/lenguajes/union`, `/lenguajes/interseccion`, `/lenguajes/diferencia`, `/lenguajes/concatenacion`, `/lenguajes/complemento`, `/lenguajes/clausura_kleene` |
| 6 | `/afd/evaluar`, `/afnd/evaluar` |
| 11 | `/afd/evaluar`, `/afnd/evaluar`, `/complejidad/peor-caso`, `/complejidad/mejor-caso` |
| 12 | `/search/greedy`, `/search/star` |
| 13 | `/graph/dijkstra`, `/graph/tsp`, `/graph/tsp/greedy`, `/graph/generate`, `/search/greedy`, `/search/star` |
| 14 | `/multiply/tradicional`, `/multiply/karatsuba`, `/multiply/comparar`, `/multiply/generate` |

El formato exacto de cada petición y respuesta está en el README de cada actividad.

## Estructura

Las actividades comparten la misma organización:

```
ActividadN-.../
├── main.py            # Punto de entrada de FastAPI: crea la app y monta los routers
├── core/              # Lógica pura (sin dependencias de FastAPI)
├── routers/           # Endpoints HTTP y modelos de petición/respuesta
├── notebooks/
│   └── ejercicios.ipynb   # Desarrollo paso a paso de los ejercicios (actividades 3 y 6)
├── requirements.txt
└── README.md          # Teoría, endpoints, ejercicios y resultados
```

La Actividad 11 no tiene `notebooks/`; en su lugar incluye `ejemplos/` (el programa de
prueba `algoritmos.py` y, en `ejemplos/salida/`, los archivos anotados que devuelve la API)
e `img/` (la imagen con los algoritmos analizados).

La Actividad 12 tampoco tiene `notebooks/`. Agrega `schemas.py` (esquemas Pydantic de entrada y
salida), `ejemplos/` (los grafos de prueba, el script `pruebas.py`, que corre todas las pruebas, y
sus resultados), `img/` (las imágenes de los grafos) y `txt/` (la estructura de los grafos).

La Actividad 13 parte del código de la 12 y sigue la misma organización, sin `img/` ni `txt/`:
sus grafos de prueba se generan con el propio endpoint `/graph/generate` y quedan en
`ejemplos/grafos.json`.

La Actividad 14 sigue la misma organización: `ejemplos/pruebas.py` corre las pruebas de
funcionamiento y las mediciones, y genera las gráficas de T(N) y S(N) en `img/`.

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

# Ejecutar el notebook con el desarrollo de los ejercicios (actividades 3 y 6)
jupyter nbconvert --execute --to notebook --inplace notebooks/ejercicios.ipynb
# o abrirlo interactivamente:
jupyter notebook notebooks/ejercicios.ipynb
```

Con la API levantada, `/docs` ofrece la interfaz de Swagger para probar cada
endpoint sin escribir código.

El notebook **no necesita** el servidor levantado: usa el `TestClient` de FastAPI,
que llama a los mismos endpoints en memoria (importa `main` desde la carpeta
superior con `sys.path.append("..")`).

## Tecnologías

- **Python 3.10+** (se usa la sintaxis de tipos `X | None`; probado con 3.14)
- **FastAPI** + **Uvicorn** — API y servidor de desarrollo
- **Pydantic** — validación de las peticiones
- **Jupyter** — notebooks con el desarrollo de los ejercicios
- **httpx** — requerido por el `TestClient` de FastAPI que usan los notebooks
- **python-multipart** — recepción de archivos en los endpoints de complejidad (Actividad 11)
- **`ast`** (biblioteca estándar) — análisis estático del programa recibido en la Actividad 11
- **`heapq`** (biblioteca estándar) — cola de prioridad de la búsqueda voraz y A* (Actividad 12)
- **`tracemalloc`** (biblioteca estándar) — medición de memoria (actividades 13 y 14)
- **matplotlib** — gráficas de T(N) y S(N) (Actividad 14)
