# Actividad 15. Implementación de Técnicas de Programación Dinámica

**Nombre de la actividad:** Actividad 15. Implementación de Técnicas de Programación Dinámica:
problema del corte de varillas (`CUT_ROD`)

## Equipo

| Nombre completo | No. de cuenta |
|---|---|
| Jonathan Hernández Lazcano | 200417 |
| Camila Rodriguez Rosas | 194100 |

## Instrucciones

> La libreta anexa implementa el algoritmo `CUT_ROD` de forma **recursiva** y con **memoización**.
>
> - Implementar la función `CUT_ROD` con **tabulación** (bottom-up).
> - Realizar un **benchmark** que compare el rendimiento de las 3 técnicas variando el tamaño de la varilla.

## Descripción

Todo el desarrollo está en [`programacion_dinamica.ipynb`](programacion_dinamica.ipynb), usando solo la biblioteca estándar de Python:

| Técnica | Función | T(n) | S(n) |
|---|---|---|---|
| Recursiva pura | `cut_rod` | `O(2ⁿ)` | `O(n)` (pila) |
| Memoización (top-down) | `cut_rod_memoized` / `cut_rod_aux` | `O(n²)` | `O(n)` |
| Tabulación (bottom-up) | `cut_rod_bottom_up` | `O(n²)` | `O(n)` |
| Tabulación extendida (con cortes) | `extended_cut_rod_bottom_up` + `obtener_cortes` | `O(n²)` | `O(n)` |

## Resultados

| Longitud de la varilla | Recursivo | Memoización | Tabulación | Ingreso Máximo | Cortes |
| --- | --- | --- | --- | --- | --- |
| 5 | 2.75 µs | 1.25 µs | 0.91 µs | $13 | [2, 3] |
| 10 | 78.92 µs | 3.94 µs | 2.91 µs | $30 | [10] |
| 15 | 2.50 ms | 8.09 µs | 5.63 µs | $43 | [2, 3, 10] |
| 20 | 80.81 ms | 14.74 µs | 9.96 µs | $60 | [10, 10] |
| 25 | 2.71 s | 21.86 µs | 14.32 µs | $73 | [2, 3, 10, 10] |
| 28 | 21.63 s | 27.48 µs | 18.20 µs | $82 | [2, 6, 10, 10] |
| 30 | 86.69 s | 31.18 µs | 20.21 µs | $90 | [10, 10, 10] |

El tiempo del recursivo se multiplica por ~2 con cada pulgada adicional; memoización y tabulación crecen
de forma cuadrática, y la tabulación es la más rápida al no tener el costo de las llamadas recursivas.

## Ejecución

Abrir la libreta en Jupyter, VS Code o Google Colab y ejecutar todas las celdas. La celda del benchmark tarda
cerca de 2 minutos por el caso recursivo con n = 28 y n = 30.
