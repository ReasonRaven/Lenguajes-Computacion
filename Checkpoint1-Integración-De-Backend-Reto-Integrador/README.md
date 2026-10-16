# Checkpoint 1. Integración de backend: Reto Integrador (Examen parcial #2)

Aplicación web para que usuarios no especializados (por ejemplo, estudiantes de nuevo
ingreso) experimenten con autómatas, optimización de rutas y complejidad algorítmica.
Reúne en un solo producto el trabajo de las actividades 3, 6, 11, 12 y 13.

## Integrantes

| Nombre | No. de cuenta |
|---|---|
| Jonathan Hernández Lazcano | 200417 |
| Camila Rodriguez Rosas | 194100 |
| Daniel Peña Cruz | 200818 |

## Requerimientos del reto

![Reto Integrador (Examen parcial #2)](Backend-Unificado/img/Reto%20Integrador%20%28Examen%20parcial%20%232%29.png)

## Arquitectura

El producto tiene tres capas, repartidas en dos proyectos:

| Capa | Dónde está | Qué hace |
|---|---|---|
| Cómputo determinista | [`Backend-Unificado/`](Backend-Unificado/README.md) (FastAPI) | Una sola API con los endpoints de todas las actividades, más BFS, DFS, Hill-Climbing, comparación de algoritmos y benchmark de ordenamiento |
| Interpretación y explicabilidad | `Backend-Unificado/core/explicaciones.py` | Cada respuesta trae un campo `explicacion` con el proceso seguido con esos datos y su base teórica |
| Interfaz gráfica | [`Frontend/`](Frontend/README.md) (React + Vite) | Formularios, editor de autómatas, grafos con la ruta resaltada, tablas comparativas y gráficas |

```
Navegador ──▶ Frontend (Vite, :5173) ──/api/*──▶ Backend-Unificado (FastAPI, :8000)
```

En desarrollo, Vite reenvía las peticiones `/api/*` al backend quitando el prefijo `/api`
(`Frontend/vite.config.js`).

## Módulos

| Módulo | Contenido | Endpoints principales |
|---|---|---|
| **1. Traductor de lenguajes y verificador de reglas** | Operaciones con cadenas y lenguajes; evaluación de AFD, AFND y AFND-ε | `/cadenas/*`, `/lenguajes/*`, `/afd/evaluar`, `/afnd/evaluar`, `/afnd-e/evaluar` |
| **2. Asistente de logística y optimización** | BFS, DFS, Hill-Climbing, voraz, A*, Dijkstra, agente viajero (exacto y voraz), comparación sobre el mismo grafo y generador de grafos | `/graph/bfs`, `/graph/dfs`, `/graph/hill-climbing`, `/graph/compare`, `/search/greedy`, `/search/star`, `/graph/dijkstra`, `/graph/tsp`, `/graph/tsp/greedy`, `/graph/generate` |
| **3. Auditoría de escalabilidad y benchmark** | Benchmark de 8 algoritmos de ordenamiento, escalabilidad contra *n* y análisis Big-O / Big-Ω de un programa en Python | `/benchmark/ordenamiento`, `/benchmark/escalabilidad`, `/complejidad/peor-caso`, `/complejidad/mejor-caso` |

El detalle de cada endpoint (origen, entradas y límites) está en el
[README del backend](Backend-Unificado/README.md); el de cada pantalla, en el
[README del frontend](Frontend/README.md).

## Estructura

```
Checkpoint1-Integración-De-Backend-Reto-Integrador/
├── Backend-Unificado/
│   ├── main.py            # Crea la app y monta los routers de los 3 módulos
│   ├── schemas.py         # Esquemas Pydantic de grafos, comparación y benchmark
│   ├── core/              # Lógica pura (algoritmos y explicaciones), sin FastAPI
│   ├── routers/           # Endpoints HTTP
│   ├── img/               # Requerimientos del reto
│   └── requirements.txt
├── Frontend/
│   ├── vite.config.js     # Proxy /api → backend
│   ├── package.json
│   └── src/               # App, módulos (Inicio, Modulo1…3) y componentes
└── README.md
```

## Cómo ejecutar

Se necesitan **Python 3.10+** y **Node.js 18+**, y dos terminales.

```bash
# Terminal 1: backend (http://127.0.0.1:8000, documentación en /docs)
cd Backend-Unificado
python3 -m venv .venv
source .venv/bin/activate                     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2: frontend (http://localhost:5173)
cd Frontend
npm install
npm run dev
```

Luego abrir http://localhost:5173. Para apuntar a otro backend:
`BACKEND_URL=http://host:puerto npm run dev`. Para producción, `npm run build` genera
`dist/` y `npm run preview` la sirve con el mismo proxy.

## Tecnologías

- **Backend:** Python, FastAPI, Uvicorn, Pydantic, python-multipart. Los algoritmos están
  escritos a mano con la biblioteca estándar (`heapq`, `ast`, `time`, `tracemalloc`,
  `random`).
- **Frontend:** React 18, Vite 5, Chart.js (`react-chartjs-2`) para las gráficas; los
  grafos se dibujan en SVG propio.
