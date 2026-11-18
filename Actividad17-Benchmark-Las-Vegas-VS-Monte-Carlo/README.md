# Actividad 17. Benchmark Las Vegas vs. Monte Carlo

**Nombre de la actividad:** Actividad 17. Benchmark Las Vegas vs. Monte Carlo: factorización exacta contra el
test de primalidad de Miller-Rabin (opción B, teoría de números / criptografía)

## Equipo

| Nombre completo | No. de cuenta |
|---|---|
| Jonathan Hernández Lazcano | 200417 |
| Camila Rodriguez Rosas | 194100 |

## Instrucciones

> Construir un benchmark que compare un algoritmo Las Vegas (resultado siempre correcto, tiempo variable)
> contra uno Monte Carlo (tiempo acotado, error acotado), con N ∈ {10², 10³, 10⁴, 10⁵}, tiempos en ms con
> `time.perf_counter()`, tasa de error variando k ∈ {1, 5, 10, 20, 50}, gráficas de rendimiento y de error,
> tabla comparativa (tiempo, memoria y % de error) y una conclusión analítica.

## Descripción

Todo el desarrollo está en [`benchmark_las_vegas_vs_monte_carlo.ipynb`](benchmark_las_vegas_vs_monte_carlo.ipynb).
La tarea común es decidir si un entero `n` es primo.

| Paradigma | Función | Qué hace |
|---|---|---|
| Las Vegas | `rho_pollard` | Busca un divisor con `x₀` y `c` aleatorios; si falla, reintenta (tiempo aleatorio) |
| Las Vegas | `menor_divisor`, `es_primo_exacto` | Certificación exacta por división de prueba hasta √m |
| Las Vegas | `factorizar_lv`, `es_primo_lv` | Factorización completa siempre correcta (verifica `∏ factores = n`) |
| Monte Carlo | `ronda_mr` | Una ejecución independiente de Miller-Rabin con una base dada |
| Monte Carlo | `miller_rabin` | k rondas con bases aleatorias (amplificación del éxito, error ≤ 4⁻ᵏ) |
| Análisis | `fraccion_mentirosos` | Fracción exacta de bases mentirosas fuertes (error real de una ronda) |
| Benchmark | `generar_lote`, `medir_ms`, `memoria_pico_kib` | Lotes de N enteros, tiempo con `perf_counter`, memoria con `tracemalloc` |

La suite de pruebas (`unittest`, 10 pruebas) compara ambos algoritmos contra una criba de Eratóstenes para
todo n < 10⁵ y revisa casos borde, potencias de primos, números de Carmichael y la cota ¼ de Rabin.

Archivos generados al ejecutar la libreta: `grafica_tiempo_vs_N.png`, `grafica_error_vs_k.png`,
`grafica_variabilidad_lv.png` y `tabla_comparativa.csv`.

## Resultados

N = tamaño del lote (enteros impares aleatorios de [10⁶, 10⁷)). Monte Carlo usa k = 10. Media de R repeticiones
con semillas distintas.

| N | R | Las Vegas (ms) | Monte Carlo (ms) | Aceleración | Memoria LV / MC (KiB) | Error LV | Error MC |
|---|---|---|---|---|---|---|---|
| 10² | 30 | 4.57 ± 0.09 | 0.19 ± 0.01 | 24.3× | 3.5 / 3.4 | 0 % | 0 % |
| 10³ | 15 | 51.63 ± 0.95 | 1.74 ± 0.04 | 29.7× | 11.2 / 11.1 | 0 % | 0 % |
| 10⁴ | 7 | 527.65 ± 7.11 | 18.84 ± 0.40 | 28.0× | 86.7 / 85.7 | 0 % | 0 % |
| 10⁵ | 3 | 5,370.47 ± 17.09 | 194.11 ± 3.00 | 27.7× | 786.2 / 784.7 | 0 % | 0 % |

**Error vs. número de rondas k** (conjunto difícil: números de Carmichael y semiprimos (2m+1)(4m+1);
200,000 ensayos por k):

| k | Errores | Error empírico | Error predicho media(fₙᵏ) | Cota 4⁻ᵏ |
|---|---|---|---|---|
| 1 | 24,930 | 12.46 % | 12.44 % | 25 % |
| 5 | 41 | 0.0205 % | 0.0197 % | 0.098 % |
| 10 | 0 | 0 % | 1.2·10⁻⁵ % | 9.5·10⁻⁵ % |
| 20 | 0 | 0 % | 6.9·10⁻¹² % | 9.1·10⁻¹¹ % |
| 50 | 0 | 0 % | 2.3·10⁻³⁰ % | 7.9·10⁻²⁹ % |

Monte Carlo fue ≈ 28× más rápido sin ningún error en 388,000 clasificaciones con entradas típicas. En el peor
caso, el error baja de forma geométrica con k, coincide con la predicción exacta y queda bajo la cota 4⁻ᵏ.
Sobre una misma entrada, el tiempo de Las Vegas varía según la semilla (para 99991·99989 va de 98 a 446 µs),
pero la respuesta nunca cambia.

La conclusión completa (en qué casos reales conviene sacrificar certeza por velocidad) está al final de la libreta.

## Ejecución

Requiere `numpy`, `pandas` y `matplotlib`. Abrir la libreta en Jupyter, VS Code o Google Colab y ejecutar todas
las celdas (tarda alrededor de 1 minuto y 15 segundos). Los tiempos absolutos dependen de la máquina.
