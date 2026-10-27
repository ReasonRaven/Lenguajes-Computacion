"""Pruebas de la Actividad 14 contra la API, en memoria con el TestClient de
FastAPI (no hace falta levantar el servidor).

Uso, desde la carpeta de la actividad:

    python ejemplos/pruebas.py

1. Pruebas de funcionamiento: multiplica con las tres variantes (tradicional,
   Karatsuba puro y Karatsuba híbrido) los números de 20, 50 y 100 dígitos,
   casos borde y cientos de pares aleatorios, y comprueba que todas den lo
   mismo que la multiplicación nativa de Python (la referencia).
2. Mide T(N) y S(N) de cada variante con N = 20, 50, 100 (los que pide la
   actividad) y 200, 500, 1000, 2000 para ver la tendencia.
3. Estima el exponente de crecimiento con un ajuste log-log.
4. Mide el efecto del umbral de la variante híbrida con N = 1000.
5. Guarda todo en ejemplos/resultados.json, genera las gráficas de img/ e
   imprime las tablas en markdown del README.

Los tiempos y la memoria cambian un poco entre ejecuciones y entre equipos.
"""

import json
import math
import random
import sys
import warnings
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parent))

# Aviso de Starlette sobre httpx, ajeno a la actividad
warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient`")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

IMG = CARPETA.parent / "img"
TAMANOS = [20, 50, 100, 200, 500, 1000, 2000]
OBLIGATORIOS = {20, 50, 100}
UMBRALES = [1, 2, 4, 8, 16, 32, 64, 128, 256]
VARIANTES = ["Tradicional", "Karatsuba puro", "Karatsuba híbrido"]

cliente = TestClient(app)


def post(ruta: str, cuerpo: dict, esperado: int = 200) -> dict:
    respuesta = cliente.post(ruta, json=cuerpo)
    assert respuesta.status_code == esperado, (respuesta.status_code, respuesta.text)
    return respuesta.json()


def generar(n: int) -> tuple[str, str]:
    numeros = post("/multiply/generate", {"n": n, "semilla": n})
    assert len(numeros["a"]) == len(numeros["b"]) == n
    return numeros["a"], numeros["b"]


def repeticiones(n: int) -> int:
    """Más repeticiones donde una sola medición es ruidosa (microsegundos)."""
    return 50 if n <= 100 else 10 if n <= 500 else 3


def comparar(a: str, b: str, reps: int = 1) -> dict:
    """POST /multiply/comparar y verifica el producto contra Python."""
    r = post("/multiply/comparar", {"a": a, "b": b, "repeticiones": reps})
    assert r["coinciden"], (a, b)
    referencia = str(int(a) * int(b))
    assert all(x["producto"] == referencia for x in r["resultados"]), (a, b)
    return r


# ---------------------------------------------------------------------------
# 1. Pruebas de funcionamiento
# ---------------------------------------------------------------------------


def pruebas_funcionamiento() -> dict:
    principales = {}
    for n in sorted(OBLIGATORIOS):
        a, b = generar(n)
        r = comparar(a, b)
        principales[n] = {"a": a, "b": b, "producto": r["producto"]}

    bordes = [
        ("0", "0"),
        ("0", "98765432109876543210"),
        ("7", "8"),
        ("1234", "5678"),  # ejemplo a mano del README
        ("9" * 100, "9" * 100),  # máximo acarreo
        ("1" + "0" * 99, "1" + "0" * 49),  # potencias de 10
        ("-" + "3" * 50, "4" * 20),  # signo y longitudes distintas
        ("-123456789", "-987654321"),
        ("000000123", "0045"),  # ceros a la izquierda
        ("9" * 100, "1"),  # 100 dígitos × 1 dígito
    ]
    for a, b in bordes:
        comparar(a, b)

    aleatorio = random.Random(14)
    for _ in range(300):
        a = str(aleatorio.randint(0, 10 ** aleatorio.randint(1, 150)))
        b = str(aleatorio.randint(0, 10 ** aleatorio.randint(1, 150)))
        if aleatorio.random() < 0.3:
            a = "-" + a
        comparar(a, b)

    errores = [{"a": "12a", "b": "3"}, {"a": "", "b": "3"}, {"a": "1.5", "b": "2"}]
    for cuerpo in errores:
        post("/multiply/karatsuba", cuerpo, esperado=422)
    post("/multiply/karatsuba", {"a": "12", "b": "3", "umbral": 0}, esperado=422)

    return {
        "principales": principales,
        "casos_borde": len(bordes),
        "aleatorios": 300,
        "entradas_invalidas": len(errores) + 1,
    }


# ---------------------------------------------------------------------------
# 2-4. Mediciones
# ---------------------------------------------------------------------------


def medir_tamanos() -> list[dict]:
    filas = []
    for n in TAMANOS:
        a, b = generar(n)
        r = comparar(a, b, repeticiones(n))
        fila = {"n": n, "aceleracion_puro": r["aceleracion_puro"],
                "aceleracion_hibrido": r["aceleracion_hibrido"],
                "ahorro_multiplicaciones": r["ahorro_multiplicaciones"]}
        for nombre, res in zip(VARIANTES, r["resultados"]):
            fila[nombre] = {
                k: res[k]
                for k in ("tiempo_ms", "memoria_kb", "multiplicaciones", "llamadas_recursivas",
                          "profundidad")
            }
        filas.append(fila)
        print(f"  N = {n:>4}: listo", file=sys.stderr)
    return filas


def exponente(xs: list[float], ys: list[float]) -> float:
    """Pendiente de la recta de mínimos cuadrados de log y contra log x."""
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)


def ajustes(filas: list[dict]) -> dict:
    grandes = [f for f in filas if f["n"] >= 100]  # con N chico domina el costo fijo
    resultado = {}
    for v in VARIANTES:
        resultado[v] = {
            "multiplicaciones": round(
                exponente([f["n"] for f in filas], [f[v]["multiplicaciones"] for f in filas]), 3
            ),
            "tiempo": round(
                exponente([f["n"] for f in grandes], [f[v]["tiempo_ms"] for f in grandes]), 3
            ),
        }
    return resultado


def medir_umbrales(n: int = 1000) -> list[dict]:
    a, b = generar(n)
    filas = []
    for umbral in UMBRALES:
        r = post("/multiply/karatsuba", {"a": a, "b": b, "umbral": umbral, "repeticiones": 3})
        assert r["producto"] == str(int(a) * int(b))
        filas.append({k: r[k] for k in ("umbral", "tiempo_ms", "memoria_kb", "multiplicaciones",
                                         "llamadas_recursivas", "profundidad")})
    return filas


# ---------------------------------------------------------------------------
# 5. Gráficas y tablas
# ---------------------------------------------------------------------------

# Paleta categórica validada (skill dataviz): azul, naranja, aqua, siempre en
# este orden; además del color cada serie tiene su propio marcador y estilo.
COLORES = {"Tradicional": "#2a78d6", "Karatsuba puro": "#eb6834", "Karatsuba híbrido": "#1baf7a"}
MARCADORES = {"Tradicional": "o", "Karatsuba puro": "s", "Karatsuba híbrido": "^"}
LINEAS = {"Tradicional": "-", "Karatsuba puro": "--", "Karatsuba híbrido": "-."}


def graficar(filas: list[dict]) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    IMG.mkdir(exist_ok=True)
    ns = [f["n"] for f in filas]
    graficas = [
        ("tiempo.png", "tiempo_ms", "T(N): tiempo de ejecución (ms)"),
        ("memoria.png", "memoria_kb", "S(N): pico de memoria (KB)"),
        ("multiplicaciones.png", "multiplicaciones", "Multiplicaciones de un dígito"),
    ]
    for archivo, campo, titulo in graficas:
        fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=150)
        fig.patch.set_facecolor("#fcfcfb")
        ax.set_facecolor("#fcfcfb")
        for v in VARIANTES:
            ys = [f[v][campo] for f in filas]
            ax.plot(ns, ys, LINEAS[v], color=COLORES[v], marker=MARCADORES[v], markersize=7,
                    linewidth=2, label=v)
            ax.annotate(v, (ns[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=9, color="#52514e")
        if campo == "multiplicaciones":
            ax.plot(ns, [n**2 for n in ns], ":", color="#8a8984", linewidth=1, label="n²")
            ax.plot(ns, [n**math.log2(3) for n in ns], ":", color="#b5b4ae", linewidth=1,
                    label="n^1.585")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns])
        ax.minorticks_off()
        ax.set_xlabel("N (dígitos de cada factor)", color="#52514e")
        ax.set_title(titulo, loc="left", color="#0b0b0b", fontsize=12)
        ax.grid(True, color="#e6e5e0", linewidth=0.8)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        for lado in ("left", "bottom"):
            ax.spines[lado].set_color("#b5b4ae")
        ax.tick_params(colors="#52514e", labelsize=9)
        ax.legend(frameon=False, fontsize=9, loc="upper left")
        ax.set_xlim(right=ns[-1] * 2.6)  # espacio para las etiquetas directas
        fig.tight_layout()
        fig.savefig(IMG / archivo)
        plt.close(fig)


def tabla_tamanos(filas: list[dict], campo: str, fmt: str) -> str:
    lineas = ["| N | " + " | ".join(VARIANTES) + " |", "|---:|" + "---:|" * len(VARIANTES)]
    for f in filas:
        n = f"**{f['n']}**" if f["n"] in OBLIGATORIOS else str(f["n"])
        lineas.append(f"| {n} | " + " | ".join(format(f[v][campo], fmt) for v in VARIANTES) + " |")
    return "\n".join(lineas)


def tabla_aceleracion(filas: list[dict]) -> str:
    lineas = ["| N | Puro vs tradicional | Híbrido vs tradicional | Multiplicaciones ahorradas (puro) |",
              "|---:|---:|---:|---:|"]
    for f in filas:
        lineas.append(f"| {f['n']} | {f['aceleracion_puro']:.2f}× | {f['aceleracion_hibrido']:.2f}× "
                      f"| {f['ahorro_multiplicaciones']:.1%} |")
    return "\n".join(lineas)


def tabla_umbrales(filas: list[dict]) -> str:
    lineas = ["| Umbral | Tiempo (ms) | Memoria (KB) | Multiplicaciones | Llamadas | Profundidad |",
              "|---:|---:|---:|---:|---:|---:|"]
    for f in filas:
        lineas.append(f"| {f['umbral']} | {f['tiempo_ms']:.2f} | {f['memoria_kb']:.1f} | "
                      f"{f['multiplicaciones']:,} | {f['llamadas_recursivas']:,} | {f['profundidad']} |")
    return "\n".join(lineas)


def main() -> None:
    print("1. Pruebas de funcionamiento...", file=sys.stderr)
    funcionamiento = pruebas_funcionamiento()
    print("   todas las variantes coinciden con la referencia", file=sys.stderr)

    print("2. Midiendo T(N) y S(N)...", file=sys.stderr)
    filas = medir_tamanos()
    print("3. Ajuste log-log...", file=sys.stderr)
    exponentes = ajustes(filas)
    print("4. Umbral de la híbrida (N = 1000)...", file=sys.stderr)
    umbrales = medir_umbrales()

    (CARPETA / "resultados.json").write_text(
        json.dumps({"funcionamiento": funcionamiento, "mediciones": filas,
                    "exponentes": exponentes, "umbrales": umbrales},
                   ensure_ascii=False, indent=2) + "\n"
    )
    graficar(filas)

    print("\n### Productos de las pruebas obligatorias\n")
    for n, p in funcionamiento["principales"].items():
        print(f"**N = {n}**\n\n```\na = {p['a']}\nb = {p['b']}\na × b = {p['producto']}\n```\n")
    print("### T(N): tiempo (ms, mediana)\n\n" + tabla_tamanos(filas, "tiempo_ms", ".4f"))
    print("\n### S(N): memoria (KB, pico)\n\n" + tabla_tamanos(filas, "memoria_kb", ".3f"))
    print("\n### Multiplicaciones de un dígito\n\n" + tabla_tamanos(filas, "multiplicaciones", ","))
    print("\n### Llamadas recursivas\n\n" + tabla_tamanos(filas, "llamadas_recursivas", ","))
    print("\n### Profundidad\n\n" + tabla_tamanos(filas, "profundidad", "d"))
    print("\n### Aceleración\n\n" + tabla_aceleracion(filas))
    print("\n### Exponentes (ajuste log-log)\n")
    print("| Variante | Multiplicaciones | Tiempo (N ≥ 100) |\n|---|---:|---:|")
    for v, e in exponentes.items():
        print(f"| {v} | {e['multiplicaciones']} | {e['tiempo']} |")
    print("\n### Umbral (N = 1000)\n\n" + tabla_umbrales(umbrales))


if __name__ == "__main__":
    main()
