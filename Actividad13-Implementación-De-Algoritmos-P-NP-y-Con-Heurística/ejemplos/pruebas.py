"""Pruebas de la Actividad 13 contra la API, en memoria con el TestClient de
FastAPI (no hace falta levantar el servidor).

Uso, desde la carpeta de la actividad:

    python ejemplos/pruebas.py

1. Genera los grafos de 5, 10 y 15 nodos con POST /graph/generate y los
   guarda en ejemplos/grafos.json.
2. Corre Dijkstra, TSP exacto y TSP voraz sobre cada uno y comprueba los
   resultados contra soluciones de referencia independientes:
   Floyd-Warshall para Dijkstra y fuerza bruta (todas las permutaciones) para
   el TSP exacto en los grafos donde es viable.
3. Corre los casos adicionales (la voraz sin salida, escalabilidad, errores).
4. Guarda todas las respuestas en ejemplos/resultados.json e imprime las
   tablas en markdown del README.

Los tiempos y la memoria cambian un poco entre ejecuciones y entre equipos.
"""

import json
import math
import sys
import warnings
from itertools import permutations
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parent))

# Aviso de Starlette sobre httpx, ajeno a la actividad
warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient`")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

# Parámetros de POST /graph/generate para cada grafo de prueba, y el par
# origen/destino de Dijkstra (del primer al último nodo).
GRAFOS = {
    "grafo-5": ({"n": 5, "densidad": 0.7, "semilla": 5}, "A", "E"),
    "grafo-10": ({"n": 10, "densidad": 0.7, "semilla": 7}, "A", "J"),
    "grafo-15": ({"n": 15, "densidad": 0.7, "semilla": 4}, "A", "O"),
}
ENDPOINTS = {"dijkstra": "Dijkstra", "tsp": "TSP exacto", "tsp/greedy": "TSP voraz"}
MAX_FUERZA_BRUTA = 10  # 9! = 362 880 permutaciones; con 15 nodos serían 14! ≈ 8.7·10¹⁰

cliente = TestClient(app)


def post(ruta: str, cuerpo: dict, esperado: int = 200) -> dict:
    respuesta = cliente.post(ruta, json=cuerpo)
    assert respuesta.status_code == esperado, (respuesta.status_code, respuesta.text)
    return respuesta.json()


# ---------------------------------------------------------------------------
# Soluciones de referencia, independientes de core/
# ---------------------------------------------------------------------------


def matriz_pesos(lista: dict, dirigido: bool) -> tuple[list[str], list[list[float]]]:
    nodos = list(lista)
    i = {nodo: k for k, nodo in enumerate(nodos)}
    w = [[math.inf] * len(nodos) for _ in nodos]
    for u, vecinos in lista.items():
        for v, peso in vecinos:
            w[i[u]][i[v]] = min(w[i[u]][i[v]], peso)
            if not dirigido:
                w[i[v]][i[u]] = min(w[i[v]][i[u]], peso)
    return nodos, w


def floyd_warshall(lista: dict, dirigido: bool, origen: str, destino: str) -> float:
    nodos, d = matriz_pesos(lista, dirigido)
    n = len(nodos)
    for k in range(n):
        d[k][k] = 0
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d[nodos.index(origen)][nodos.index(destino)]


def tsp_fuerza_bruta(lista: dict, dirigido: bool, origen: str) -> float:
    nodos, w = matriz_pesos(lista, dirigido)
    o = nodos.index(origen)
    resto = [k for k in range(len(nodos)) if k != o]
    mejor = math.inf
    for orden in permutations(resto):
        ciclo = (o, *orden, o)
        mejor = min(mejor, sum(w[a][b] for a, b in zip(ciclo, ciclo[1:])))
    return mejor


def costo_ruta(lista: dict, dirigido: bool, ruta: list[str]) -> float:
    nodos, w = matriz_pesos(lista, dirigido)
    i = {nodo: k for k, nodo in enumerate(nodos)}
    return sum(w[i[a]][i[b]] for a, b in zip(ruta, ruta[1:]))


def es_ciclo_hamiltoniano(ruta: list[str], nodos: list[str], origen: str) -> bool:
    return ruta[0] == ruta[-1] == origen and sorted(ruta[:-1]) == sorted(nodos)


# ---------------------------------------------------------------------------
# Formato de las tablas
# ---------------------------------------------------------------------------


def fmt(valor) -> str:
    return "—" if valor is None else f"{valor:g}"


def fmt_ruta(r: dict) -> str:
    return " → ".join(r["ruta"]) if r["ruta"] else "—"


ENCABEZADO = (
    "| Algoritmo | Clase | Solución | Ruta | Costo | Nodos recorridos | Operaciones "
    "| Tiempo (ms) | Memoria (KB) |\n|---|---|---|---|---|---|---|---|---|"
)


def fila(nombre: str, r: dict) -> str:
    return (
        f"| {nombre} | {r['clase']} | {r['solucion']} | {fmt_ruta(r)} | {fmt(r['costo'])} "
        f"| {r['nodos_recorridos']} | {r['operaciones']} | {r['tiempo_ms']:.4f} "
        f"| {r['memoria_kb']:.3f} |"
    )


# ---------------------------------------------------------------------------
# Pruebas principales: grafos de 5, 10 y 15 nodos × 3 algoritmos
# ---------------------------------------------------------------------------


def pruebas_principales(grafos: dict, resultados: dict) -> None:
    resumen = [
        "| Grafo | Aristas | Dijkstra (costo · recorridos · ms · KB) "
        "| TSP exacto | TSP voraz | Voraz / óptimo |",
        "|---|---|---|---|---|---|",
    ]
    for nombre, (parametros, origen, destino) in GRAFOS.items():
        g = grafos[nombre] = post("/graph/generate", parametros)
        lista, dirigido = g["lista_adyacencia"], g["dirigido"]
        cuerpo = {"lista_adyacencia": lista, "dirigido": dirigido, "origen": origen}
        r = resultados[nombre] = {
            "dijkstra": post("/graph/dijkstra", {**cuerpo, "destino": destino}),
            "tsp": post("/graph/tsp", cuerpo),
            "tsp/greedy": post("/graph/tsp/greedy", cuerpo),
        }

        # Dijkstra: el costo es el de Floyd-Warshall y la ruta cuesta lo que dice
        dij = r["dijkstra"]
        assert dij["solucion"]
        assert dij["costo"] == floyd_warshall(lista, dirigido, origen, destino)
        assert costo_ruta(lista, dirigido, dij["ruta"]) == dij["costo"]

        # TSP: ciclos hamiltonianos válidos; el exacto es óptimo y la voraz no lo mejora
        exacto, voraz = r["tsp"], r["tsp/greedy"]
        for t in (exacto, voraz):
            assert t["solucion"] and es_ciclo_hamiltoniano(t["ruta"], list(lista), origen)
            assert costo_ruta(lista, dirigido, t["ruta"]) == t["costo"]
        if g["n"] <= MAX_FUERZA_BRUTA:
            assert exacto["costo"] == tsp_fuerza_bruta(lista, dirigido, origen)
        assert voraz["costo"] >= exacto["costo"]
        assert voraz["nodos_recorridos"] == g["n"]

        print(f"\n### {nombre}: {g['n']} nodos, {g['num_aristas']} aristas\n\n{ENCABEZADO}")
        for endpoint, algoritmo in ENDPOINTS.items():
            print(fila(algoritmo, r[endpoint]))
        resumen.append(
            f"| {g['n']} nodos | {g['num_aristas']} "
            f"| {fmt(dij['costo'])} · {dij['nodos_recorridos']} · {dij['tiempo_ms']:.4f} "
            f"· {dij['memoria_kb']:.3f} "
            f"| {fmt(exacto['costo'])} · {exacto['nodos_recorridos']} "
            f"· {exacto['tiempo_ms']:.4f} · {exacto['memoria_kb']:.3f} "
            f"| {fmt(voraz['costo'])} · {voraz['nodos_recorridos']} "
            f"· {voraz['tiempo_ms']:.4f} · {voraz['memoria_kb']:.3f} "
            f"| {voraz['costo'] / exacto['costo']:.3f} |"
        )
    print("\n### Resumen\n")
    print("\n".join(resumen))


# ---------------------------------------------------------------------------
# Casos adicionales
# ---------------------------------------------------------------------------


def casos_adicionales(resultados: dict) -> None:
    # 1. La voraz se queda sin salida aunque el ciclo sí existe
    g = post("/graph/generate", {"n": 10, "densidad": 0.7, "semilla": 1})
    cuerpo = {"lista_adyacencia": g["lista_adyacencia"], "dirigido": False, "origen": "A"}
    caso = resultados["voraz_sin_salida"] = {
        "grafo": g,
        "tsp": post("/graph/tsp", cuerpo),
        "tsp/greedy": post("/graph/tsp/greedy", cuerpo),
    }
    assert caso["tsp"]["solucion"] and not caso["tsp/greedy"]["solucion"]
    print(f"\n### Voraz sin salida: 10 nodos, semilla 1\n\n{ENCABEZADO}")
    print(fila("TSP exacto", caso["tsp"]))
    print(fila("TSP voraz", caso["tsp/greedy"]))
    print(f"\nMotivo: {caso['tsp/greedy']['motivo']}")

    # 2. Escalabilidad: grafos completos de 4 a 18 nodos
    caso = resultados["escalabilidad"] = {}
    print(
        "\n### Escalabilidad (grafos completos, semilla 1)\n\n"
        "| n | Dijkstra (ms) | TSP exacto: estados | TSP exacto (ms) | TSP exacto (KB) "
        "| TSP voraz (ms) | TSP voraz (KB) | Voraz / óptimo |\n"
        "|---|---|---|---|---|---|---|---|"
    )
    for n in (4, 6, 8, 10, 12, 14, 16, 18):
        g = post("/graph/generate", {"n": n, "densidad": 1, "semilla": 1})
        cuerpo = {"lista_adyacencia": g["lista_adyacencia"], "dirigido": False, "origen": "A"}
        dij = post("/graph/dijkstra", {**cuerpo, "destino": list(g["lista_adyacencia"])[-1]})
        ex = post("/graph/tsp", cuerpo)
        vz = post("/graph/tsp/greedy", cuerpo)
        caso[n] = {"dijkstra": dij, "tsp": ex, "tsp/greedy": vz}
        print(
            f"| {n} | {dij['tiempo_ms']:.4f} | {ex['nodos_recorridos']} "
            f"| {ex['tiempo_ms']:.4f} | {ex['memoria_kb']:.3f} | {vz['tiempo_ms']:.4f} "
            f"| {vz['memoria_kb']:.3f} | {vz['costo'] / ex['costo']:.3f} |"
        )

    # 3. Errores de validación (422)
    caso = resultados["errores"] = {}
    grande = post("/graph/generate", {"n": 19, "densidad": 1, "semilla": 1})
    errores = {
        "tsp_exacto_19_nodos": ("/graph/tsp", {**grande, "origen": "A"}),
        "origen_inexistente": (
            "/graph/dijkstra",
            {"lista_adyacencia": grande["lista_adyacencia"], "origen": "Z", "destino": "A"},
        ),
        "peso_negativo": (
            "/graph/dijkstra",
            {"aristas": [["A", "B", -3]], "origen": "A", "destino": "B"},
        ),
    }
    print()
    for nombre, (ruta, cuerpo) in errores.items():
        caso[nombre] = post(ruta, cuerpo, esperado=422)
        print(f"422 {nombre}: {caso[nombre]['detail'][0]['msg']}")

    # Con 19 nodos la voraz sí responde
    vz = post("/graph/tsp/greedy", {**grande, "origen": "A"})
    assert vz["solucion"]
    caso["tsp_voraz_19_nodos"] = vz
    print(f"TSP voraz con 19 nodos: costo {vz['costo']:g} en {vz['tiempo_ms']:.4f} ms")


def main() -> None:
    grafos: dict = {}
    resultados: dict = {"pruebas": {}, "adicionales": {}}
    pruebas_principales(grafos, resultados["pruebas"])
    casos_adicionales(resultados["adicionales"])

    (CARPETA / "grafos.json").write_text(
        json.dumps(grafos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (CARPETA / "resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("\nTodas las comprobaciones pasaron. Grafos en grafos.json, respuestas en resultados.json.")


if __name__ == "__main__":
    main()
