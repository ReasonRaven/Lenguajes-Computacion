# Actividad 16. Análisis de Desempeño de Algoritmo Paralelo

**Nombre de la actividad:** Actividad 16. Análisis de desempeño de algoritmo paralelo: simulación
meteorológica SPMD con *ghost cells* y `multiprocessing.Pipe`

## Equipo

| Nombre completo | No. de cuenta |
|---|---|
| Jonathan Hernández Lazcano | 200417 |
| Camila Rodriguez Rosas | 194100 |

## Instrucciones

> Ejecutar la simulación variando el número de procesos (P ∈ {1, 2, 4, 8}) y registrar los tiempos de ejecución
> para completar la tabla de evaluación (Tp, Sp = T1/Tp, Ep = Sp/P), y responder las preguntas sobre
> *ghost cells*, balanceo de carga y la Ley de Amdahl.

## Descripción

Todo el desarrollo está en [`practica_simulacion_meteorologica.ipynb`](practica_simulacion_meteorologica.ipynb),
organizado según la metodología de Foster:

| Fase | Función | Qué hace |
|---|---|---|
| 1. Particionamiento | `particion_filas`, `inicializacion_subdominio` | Divide la malla N×N en P franjas horizontales con *ghost cells* |
| 2. Comunicación | `intercambio_ghost_cells` | Intercambia la fila de borde con los vecinos Norte/Sur por `Pipe` |
| 3. Agrupamiento | `calcular_paso_atmosferico` | Stencil de 5 puntos vectorizado con NumPy |
| 4. Integración | `worker_spmd` | Ciclo SPMD; mide tiempo de comunicación y de cómputo |
| 5. Evaluación | `ejecutar_simulacion`, `benchmark` | Lanza P procesos, mide Tp y reensambla la malla |

Correcciones hechas a la libreta original para que pudiera ejecutarse:

- `inicializacion_subdominio` recibe el **rank** para ubicar su franja en el dominio global y reparte bien las
  filas cuando N no es divisible entre P (500/8). Además se vectorizó la inicialización.
- `intercambio_ghost_cells`: la frontera física se aplica solo en los bordes **sin** vecino. Antes asignaba un
  vector a un escalar.
- `calcular_paso_atmosferico`: se corrigieron los *slices* del stencil, que no coincidían en forma.
- `worker_spmd`: se corrigió `historico.append((step, ...))` y ahora regresa la franja final y los tiempos.
- Se agregó el orquestador (`ejecutar_simulacion`), que antes faltaba, y se verifica que la malla calculada en
  paralelo sea idéntica a la secuencial.

## Resultados

Mediana de 3 repeticiones, 1000 pasos de tiempo, en una máquina de 12 núcleos.

**N = 500 (tabla de evaluación)**

| Procesos (P) | Tiempo Total Tp (s) | Aceleración (Sp = T1/Tp) | Eficiencia (Ep = Sp/P) | % comunicación |
|---|---|---|---|---|
| 1 (Secuencial) | 0.430 | 1.00 | 100% | 0.2% |
| 2 | 0.256 | 1.68 | 84% | 7.9% |
| 4 | 0.175 | 2.45 | 61% | 22.1% |
| 8 | 0.170 | 2.53 | 32% | 53.7% |

**N = 100 (comparación)**

| Procesos (P) | Tiempo Total Tp (s) | Aceleración (Sp = T1/Tp) | Eficiencia (Ep = Sp/P) | % comunicación |
|---|---|---|---|---|
| 1 (Secuencial) | 0.027 | 1.00 | 100% | 2.8% |
| 2 | 0.040 | 0.66 | 33% | 58.6% |
| 4 | 0.050 | 0.54 | 14% | 78.6% |
| 8 | 0.075 | 0.36 | 4% | 89.1% |

Con N=500 el paralelismo sí acelera el programa, aunque de P=4 a P=8 casi ya no mejora porque más de la mitad
del tiempo se va en comunicación. Con N=100 el paralelismo lo hace **más lento**: casi todo el tiempo se va en
el intercambio por `pipes`.

## Preguntas

**1. ¿Cómo afecta el tamaño de la franja de Ghost Cells al tiempo total con N = 500?**
Cada mensaje es una fila de N+2 `float64` (≈ 4 KB con N=500). La comunicación crece O(N) y el cómputo
O(N²/P), así que al aumentar N baja la relación comunicación/cómputo: con P=8 pasa de 89 % (N=100) a 54 %
(N=500), y la aceleración sube de 0.36× a 2.53×. El costo dominante es la latencia y la sincronización por
mensaje más que los bytes enviados. Para reducirlo se pueden usar franjas fantasma más anchas (intercambiar
cada *k* pasos), comunicación asíncrona o memoria compartida.

**2. Tormenta severa en un subdominio: ¿por qué falla la asignación estática y qué balanceo dinámico usar?**
La partición estática supone que todas las celdas cuestan lo mismo. La franja con la tormenta se vuelve la más
lenta y, como hay sincronización en cada paso por las *ghost cells*, todos los procesos esperan al más lento.
Conviene usar un balanceo dinámico: dividir el dominio en bloques más finos y repartirlos bajo demanda
(*work pool*, por ejemplo `Pool.imap_unordered` con `chunksize` pequeño), aplicar *work stealing*, o
**reparticionar de forma adaptativa** moviendo las fronteras según el costo medido de cada franja. Esta
última opción es la recomendada aquí porque conserva la localidad de las *ghost cells*.

**3. Ley de Amdahl con 10 % de comunicación inalterable:**
S_max = 1 / f = 1 / 0.10 = **10×**, sin importar cuántos procesadores se agreguen. Con P=8 el máximo teórico es
1 / (0.1 + 0.9/8) ≈ 4.71×. La aceleración medida (2.53×) queda por debajo por costos que Amdahl no considera:
creación de procesos, serialización y espera entre vecinos.

## Ejecución

Requiere `numpy`, `pandas` y `matplotlib`. Abrir la libreta en Jupyter, VS Code o Google Colab y ejecutar todas
las celdas (tarda unos 10 s). Se usa el contexto `fork` de `multiprocessing`, por lo que funciona en macOS y
Linux/Colab. En Windows no está disponible `fork`.
