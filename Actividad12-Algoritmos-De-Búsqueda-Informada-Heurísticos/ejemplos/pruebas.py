"""Pruebas de la Actividad 12 contra la API, en memoria con el TestClient de
FastAPI (no hace falta levantar el servidor).

Uso, desde la carpeta de la actividad:

    python ejemplos/pruebas.py

Corre las 3 pruebas de cada grafo con los dos algoritmos y las dos
heurísticas, más los casos adicionales; comprueba los resultados (A* debe dar
el costo óptimo, calculado aquí por fuerza bruta), guarda todas las respuestas
en ejemplos/resultados.json e imprime las tablas en markdown del README.
"""

import json
import sys
import warnings
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parent))

# Aviso de Starlette sobre httpx, ajeno a la actividad
warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient`")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

GRAFOS = json.loads((CARPETA / "grafos.json").read_text(encoding="utf-8"))

# La primera prueba de cada grafo es el origen/destino que marca su imagen.
PRUEBAS = {
    "grafo-10": [("A", "J"), ("D", "J"), ("B", "H")],
    "grafo-25": [("A", "Y"), ("B", "P"), ("D", "Q")],
    "grafo-50": [("A", "AX"), ("D", "AS"), ("B", "AA")],
}
ALGORITMOS = {"greedy": "Voraz", "star": "A*"}
HEURISTICAS = ("euclidiana", "saltos")

cliente = TestClient(app)


def peticion(grafo: str, origen: str, destino: str, heuristica: str, **extra) -> dict:
    datos = GRAFOS[grafo]
    cuerpo = {
        "lista_adyacencia": datos["lista_adyacencia"],
        "origen": origen,
        "destino": destino,
        "heuristica": heuristica,
        **extra,
    }
    if heuristica == "euclidiana":
        cuerpo["coordenadas"] = datos["coordenadas"]
    return cuerpo


def buscar(endpoint: str, cuerpo: dict, esperado: int = 200) -> dict:
    respuesta = cliente.post(f"/search/{endpoint}", json=cuerpo)
    assert respuesta.status_code == esperado, (respuesta.status_code, respuesta.text)
    return respuesta.json()


def costo_optimo(lista: dict, origen: str, destino: str) -> float | None:
    """Costo mínimo por fuerza bruta: recorre todos los caminos simples."""
    mejor = None
    pila = [(origen, 0, {origen})]
    while pila:
        nodo, costo, usados = pila.pop()
        if nodo == destino:
            mejor = costo if mejor is None else min(mejor, costo)
            continue
        for vecino, peso in lista[nodo]:
            if vecino not in usados:
                pila.append((vecino, costo + peso, usados | {vecino}))
    return mejor


# ---------------------------------------------------------------------------
# Formato de las tablas
# ---------------------------------------------------------------------------


def fmt_costo(valor) -> str:
    return "—" if valor is None else f"{valor:g}"


def fmt_ruta(r: dict) -> str:
    return " → ".join(r["ruta"]) if r["ruta"] else "—"


def fmt_t(r: dict) -> str:
    t = r["T(n)"]
    return (
        f"O({t['b']}^{t['profundidad']}) = {t['cota']} · "
        f"{t['nodos_generados']} generados · {t['tiempo_ms']:.4f} ms"
    )


def fmt_s(r: dict) -> str:
    s = r["S(n)"]
    return (
        f"O({s['b']}^{s['profundidad']}) = {s['cota']} · "
        f"{s['max_nodos_en_memoria']} en memoria (frontera máx. {s['max_frontera']})"
    )


def fila(prueba: str, r: dict, heuristica: str, algoritmo: str) -> str:
    return (
        f"| {prueba} | {algoritmo} | {heuristica} | {r['solucion']} | {fmt_ruta(r)} "
        f"| {fmt_costo(r['costo'])} | {r['nodos_visitados']} / {r['limite_nodos']} "
        f"| {fmt_t(r)} | {fmt_s(r)} |"
    )


ENCABEZADO = (
    "| Prueba | Algoritmo | Heurística | Solución | Ruta | Costo | Visitados / límite "
    "| T(n) | S(n) |\n|---|---|---|---|---|---|---|---|---|"
)


# ---------------------------------------------------------------------------
# Pruebas principales: 3 por grafo × 2 algoritmos × 2 heurísticas
# ---------------------------------------------------------------------------


def pruebas_principales(resultados: dict) -> None:
    resumen = [
        "| Grafo | Prueba | Óptimo | Voraz (euclidiana) | Voraz (saltos) "
        "| A* (euclidiana) | A* (saltos) |",
        "|---|---|---|---|---|---|---|",
    ]
    for grafo, pares in PRUEBAS.items():
        lista = GRAFOS[grafo]["lista_adyacencia"]
        print(f"\n### {grafo} ({len(lista)} nodos)\n\n{ENCABEZADO}")
        resultados[grafo] = {}
        for origen, destino in pares:
            prueba = f"{origen} → {destino}"
            optimo = costo_optimo(lista, origen, destino)
            por_prueba = resultados[grafo][f"{origen}->{destino}"] = {}
            celdas = {}
            for heuristica in HEURISTICAS:
                for endpoint, algoritmo in ALGORITMOS.items():
                    r = buscar(endpoint, peticion(grafo, origen, destino, heuristica))
                    por_prueba.setdefault(heuristica, {})[endpoint] = r

                    assert r["solucion"], (grafo, prueba, heuristica, endpoint, r["motivo"])
                    assert r["nodos_visitados"] <= r["limite_nodos"]
                    assert r["costo"] >= optimo
                    if endpoint == "star":
                        assert r["costo"] == optimo, (grafo, prueba, heuristica, r["costo"], optimo)

                    print(fila(prueba, r, heuristica, algoritmo))
                    celdas[(endpoint, heuristica)] = (
                        f"{fmt_costo(r['costo'])} ({r['nodos_visitados']} visitados)"
                    )
            resumen.append(
                f"| {len(lista)} nodos | {prueba} | {fmt_costo(optimo)} "
                f"| {celdas[('greedy', 'euclidiana')]} | {celdas[('greedy', 'saltos')]} "
                f"| {celdas[('star', 'euclidiana')]} | {celdas[('star', 'saltos')]} |"
            )
    print("\n### Resumen (costo de la ruta y nodos visitados)\n")
    print("\n".join(resumen))


# ---------------------------------------------------------------------------
# Casos adicionales
# ---------------------------------------------------------------------------


def casos_adicionales(resultados: dict) -> None:
    print(f"\n### Casos adicionales\n\n{ENCABEZADO}")

    # 1. Sin camino: J no tiene aristas de salida
    caso = resultados["sin_camino"] = {}
    for endpoint, algoritmo in ALGORITMOS.items():
        r = caso[endpoint] = buscar(endpoint, peticion("grafo-10", "J", "A", "saltos"))
        assert not r["solucion"] and "no existe camino" in r["motivo"]
        print(fila("10 nodos: J → A", r, "saltos", algoritmo))

    # 2. El límite del 80 % frente a la calidad de la heurística
    caso = resultados["limite_y_heuristica"] = {}
    for heuristica in HEURISTICAS:
        for endpoint, algoritmo in ALGORITMOS.items():
            r = buscar(endpoint, peticion("grafo-25", "B", "T", heuristica))
            caso.setdefault(heuristica, {})[endpoint] = r
            print(fila("25 nodos: B → T", r, heuristica, algoritmo))
    assert not caso["euclidiana"]["star"]["solucion"]
    assert "límite" in caso["euclidiana"]["star"]["motivo"]
    assert caso["saltos"]["star"]["costo"] == costo_optimo(
        GRAFOS["grafo-25"]["lista_adyacencia"], "B", "T"
    )

    # 3. Límite personalizado
    caso = resultados["limite_personalizado"] = {}
    for endpoint, algoritmo in ALGORITMOS.items():
        r = caso[endpoint] = buscar(
            endpoint, peticion("grafo-50", "A", "AX", "saltos", limite_nodos=5)
        )
        assert not r["solucion"] and r["nodos_visitados"] == 5
        print(fila("50 nodos: A → AX, límite 5", r, "saltos", algoritmo))

    # 4. El mismo grafo como matriz de adyacencia da el mismo resultado que como lista
    lista = GRAFOS["grafo-10"]["lista_adyacencia"]
    nodos = list(lista)
    matriz = [[dict(lista[u]).get(v, 0) for v in nodos] for u in nodos]
    caso = resultados["matriz"] = {"peticion": {"nodos": nodos, "matriz_adyacencia": matriz}}
    for endpoint in ALGORITMOS:
        como_matriz = buscar(
            endpoint,
            {"nodos": nodos, "matriz_adyacencia": matriz, "origen": "A", "destino": "J"},
        )
        como_lista = buscar(endpoint, {"lista_adyacencia": lista, "origen": "A", "destino": "J"})
        for campo in ("solucion", "ruta", "costo", "nodos_visitados", "traza"):
            assert como_matriz[campo] == como_lista[campo], campo
        caso[endpoint] = como_matriz
    print("\nMatriz de adyacencia = lista de adyacencia: OK")

    # 5. Errores de validación (422)
    caso = resultados["errores"] = {}
    errores = {
        "origen_inexistente": {"lista_adyacencia": lista, "origen": "Z", "destino": "J"},
        "euclidiana_sin_coordenadas": {
            "lista_adyacencia": lista,
            "origen": "A",
            "destino": "J",
            "heuristica": "euclidiana",
        },
    }
    for nombre, cuerpo in errores.items():
        caso[nombre] = buscar("star", cuerpo, esperado=422)
        print(f"422 {nombre}: {caso[nombre]['detail'][0]['msg']}")


def main() -> None:
    resultados: dict = {"pruebas": {}, "adicionales": {}}
    pruebas_principales(resultados["pruebas"])
    casos_adicionales(resultados["adicionales"])
    destino = CARPETA / "resultados.json"
    destino.write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nTodas las comprobaciones pasaron. Respuestas guardadas en {destino.name}.")


if __name__ == "__main__":
    main()
