# Reto Integrador (Examen parcial #2): frontend

Interfaz gráfica (React + Vite) del producto del reto integrador: una aplicación web para
que usuarios no especializados experimenten con autómatas, optimización de rutas y
complejidad algorítmica. Es la tercera capa de la arquitectura; el cómputo y las
explicaciones vienen de [`Backend-Unificado/`](../Backend-Unificado/README.md).

**Integrantes:** Jonathan Hernández Lazcano (200417) · Camila Rodriguez Rosas (194100) ·
Daniel Peña Cruz (200818)

## Cómo ejecutar

Se necesitan dos terminales: una para el backend y otra para el frontend.

```bash
# Terminal 1: backend (http://127.0.0.1:8000)
cd Backend-Unificado
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2: frontend (http://localhost:5173)
cd Frontend
npm install
npm run dev
```

En desarrollo, Vite reenvía las peticiones `/api/*` al backend en el puerto 8000
(`vite.config.js`). Para usar otro backend: `BACKEND_URL=http://host:puerto npm run dev`.
Para producción, `npm run build` genera `dist/`; `npm run preview` la sirve con el mismo
proxy.

## Qué hace cada módulo

Cada resultado incluye un panel **«¿Qué pasó y por qué?»** con la explicación del proceso
y su base teórica, generada por la capa de explicabilidad del backend.

| Módulo | Entradas | Resultados |
|---|---|---|
| **1. Traductor de lenguajes y verificador de reglas** | Editor de la tabla de transición (AFD, AFND o AFND-ε, con ejemplos precargados), cadenas, lenguajes L y M | Tarjeta aceptada/rechazada por cadena, con notación (q, w) ⊢ … y camino de aceptación; resultado de operaciones con cadenas y lenguajes |
| **2. Asistente de logística y optimización** | Grafo como aristas, JSON (lista, matriz o aristas) o generado al azar; origen, destino, heurística y algoritmos (BFS, DFS, Hill-Climbing, voraz, A*, Dijkstra) | Grafo dibujado con la ruta resaltada y el orden de visita; tabla comparativa con camino, costo, tiempo y memoria; alcance máximo coloreado por nivel; agente viajero exacto contra heurístico |
| **3. Auditoría de escalabilidad y benchmark** | Al menos 2 algoritmos de ordenamiento; lista propia o generada (n, distribución, semilla); tamaños n; archivo `.py` | Lista ordenada, tabla con tiempo, memoria, comparaciones, complejidad y clase; gráfica de barras; gráfica de tiempo contra n (lineal o logarítmica); código anotado con su complejidad |

## Estructura

```
Frontend/
├── index.html
├── vite.config.js        # Proxy /api → backend
├── package.json
└── src/
    ├── main.jsx, App.jsx  # Encabezado, navegación por módulos (#inicio, #modulo1…3)
    ├── api.js             # post() y postArchivo(); convierte los errores 422 en mensajes
    ├── useLlamada.js      # Estado de carga, error y datos de cada llamada
    ├── datos.js           # Integrantes, ejemplos precargados, catálogos y colores
    ├── styles.css         # Estilos (modo claro/oscuro, responsive)
    ├── components/        # Explicacion, GrafoSVG, TablaTransiciones, ListaInput, …
    └── modulos/           # Inicio, Modulo1, Modulo2, Modulo3
```
