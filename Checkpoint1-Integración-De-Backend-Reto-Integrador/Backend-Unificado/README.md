# Reto Integrador (Examen parcial #2): backend

Backend en **FastAPI** del producto del reto integrador: una aplicación web para que
usuarios no especializados (por ejemplo, estudiantes de nuevo ingreso) experimenten con
autómatas, optimización de rutas y complejidad algorítmica.

## Integrantes

| Nombre | No. de cuenta |
|---|---|
| Jonathan Hernández Lazcano | 200417 |
| Camila Rodriguez Rosas | 194100 |
| Daniel Peña Cruz | 200818 |

## Requerimientos del reto

![Reto Integrador (Examen parcial #2)](img/Reto%20Integrador%20%28Examen%20parcial%20%232%29.png)

La arquitectura del producto tiene tres capas. Este proyecto cubre dos:

- **Cómputo determinista (backend):** los endpoints de esta API.
- **Capa de interpretación y explicabilidad:** cada respuesta trae un campo
  `explicacion` con el proceso que se siguió con *esos* datos y la base teórica que lo
  sustenta (`core/explicaciones.py`). En los autómatas, además, cada cadena evaluada trae
  su propia `explicacion`.
- La **interfaz gráfica (frontend)** consume esta API y no forma parte de esta carpeta.

El backend parte del código de las actividades 3, 6, 11, 12 y 13. Las carpetas de esas
actividades no se modificaron.

## Módulos y endpoints

Todos son `POST` con JSON, salvo `GET /` (verificación de estado) y los de complejidad,
que reciben un archivo (`multipart/form-data`). En `/docs` aparecen agrupados por módulo y
cada endpoint trae ejemplos listos para probar.

### Módulo 1: traductor de lenguajes y verificador de reglas

| Endpoint | Qué hace | Origen |
|---|---|---|
| `/cadenas/concatenar`, `/cadenas/unir`, `/cadenas/potencia` | Operaciones con cadenas | Act. 3 |
| `/lenguajes/union`, `/interseccion`, `/diferencia`, `/concatenacion`, `/complemento`, `/clausura_kleene` | Operaciones con lenguajes | Act. 3 |
| `/afd/evaluar` | Pertenencia de cadenas en un AFD | Act. 6 |
| `/afnd/evaluar` | Pertenencia de cadenas en un AFND (con o sin λ) | Act. 6 |
| `/afnd-e/evaluar` | El mismo evaluador, bajo el nombre AFND-ε: acepta transiciones `λ`, `ε`, `lambda` o `""` | Nuevo |

### Módulo 2: asistente de logística y optimización

El grafo se puede enviar como lista de adyacencia, matriz de adyacencia o vector de aristas.

| Endpoint | Qué hace | Origen |
|---|---|---|
| `/graph/bfs` | Búsqueda en anchura. Con `destino`: la ruta con menos aristas. Sin `destino`: **alcance máximo** (cada nodo alcanzable y a cuántos saltos está) | Nuevo |
| `/graph/dfs` | Búsqueda en profundidad. Con o sin `destino`, igual que BFS | Nuevo |
| `/graph/hill-climbing` | Ascenso de colinas con heurística euclidiana o por saltos. Reporta si se atoró en un óptimo local | Nuevo |
| `/graph/compare` | Corre los algoritmos elegidos (`bfs`, `dfs`, `hill-climbing`, `greedy`, `astar`, `dijkstra`) **con el mismo grafo** y devuelve una tabla comparativa: ruta, costo, nodos, tiempo y memoria; indica el de menor costo y el más rápido | Nuevo |
| `/search/greedy`, `/search/star` | Búsqueda voraz y A* | Act. 12 |
| `/graph/dijkstra` | Camino de menor costo (P) | Act. 13 |
| `/graph/tsp`, `/graph/tsp/greedy` | Agente viajero exacto (NP-difícil) y con heurística voraz | Act. 13 |
| `/graph/generate` | Generador de grafos sintéticos | Act. 13 |

### Módulo 3: auditoría de escalabilidad y benchmark de algoritmos

Catálogo de ordenamiento: `burbuja`, `seleccion`, `insercion` (O(n²)); `merge`, `quick`,
`heap` (O(n log n)); `counting` (O(n + k), solo enteros) y `permutaciones` (fuerza bruta
O(n · n!), como contraste exponencial).

| Endpoint | Qué hace | Origen |
|---|---|---|
| `/benchmark/ordenamiento` | Ordena **la misma lista** con al menos 2 algoritmos. Recibe una lista propia (`datos`) o una generada (`n`, `distribucion`: aleatoria, ordenada, inversa o casi_ordenada, y `semilla`). Devuelve la lista ordenada y, por algoritmo, tiempo, memoria, comparaciones, intercambios, complejidad (mejor, promedio y peor caso), espacio, clase y un ranking | Nuevo |
| `/benchmark/escalabilidad` | Mide cada algoritmo con varios tamaños de `n` y devuelve una serie por algoritmo, lista para la gráfica comparativa | Nuevo |
| `/complejidad/peor-caso`, `/complejidad/mejor-caso` | Anota la complejidad Big-O o Big-Ω de un programa en Python, línea por línea | Act. 11 |

Para que una petición no deje colgado al servidor hay límites: los algoritmos O(n²)
aceptan hasta 3 000 elementos, `permutaciones` hasta 8 y los demás hasta 50 000. Si se
pasa un límite, la API responde 422 con el motivo.

## Estructura

```
Backend-Unificado/
├── main.py            # Crea la app y monta los routers de los 3 módulos
├── schemas.py         # Esquemas Pydantic de grafos, comparación y benchmark
├── core/              # Lógica pura (sin FastAPI)
│   ├── explicaciones.py   # Capa de explicabilidad
│   ├── bfs.py, dfs.py, hill_climbing.py, comparador.py   # Nuevos (módulo 2)
│   ├── ordenamiento.py    # Nuevo (módulo 3)
│   └── ...                # Código de las actividades 3, 6, 11, 12 y 13
├── routers/           # Endpoints HTTP (benchmark.py es nuevo)
├── img/               # Requerimientos del reto
├── requirements.txt
└── README.md
```

## Cómo ejecutar

```bash
cd Backend-Unificado

python3 -m venv .venv
source .venv/bin/activate                     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Documentación interactiva en http://127.0.0.1:8000/docs
uvicorn main:app --reload
```
