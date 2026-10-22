import { useMemo, useState } from "react";
import { post } from "../api.js";
import { ALGORITMOS_RUTA, COLORES, COORDENADAS_10, GRAFO_10 } from "../datos.js";
import { useLlamada } from "../useLlamada.js";
import BotonEnviar from "../components/BotonEnviar.jsx";
import ErrorMsg from "../components/ErrorMsg.jsx";
import Explicacion from "../components/Explicacion.jsx";
import GrafoSVG from "../components/GrafoSVG.jsx";
import Segmentado from "../components/Segmentado.jsx";

const fmt = (x, d = 4) => (x === null || x === undefined ? "—" : Number(x.toFixed(d)).toString());

// ---------------------------------------------------------------------------
// Conversión entre los formatos de entrada y la lista de adyacencia
// ---------------------------------------------------------------------------

function aristasATexto(lista) {
  return Object.entries(lista)
    .flatMap(([u, vs]) => vs.map(([v, w]) => `${u} ${v} ${w}`))
    .join("\n");
}

function textoALista(texto) {
  const lista = {};
  texto
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean)
    .forEach((linea, i) => {
      const partes = linea.split(/[\s,;]+/);
      if (partes.length === 1) {
        lista[partes[0]] ??= []; // nodo aislado
        return;
      }
      const [u, v, w] = partes;
      const peso = Number(w ?? 1);
      if (!v || Number.isNaN(peso)) throw new Error(`Línea ${i + 1}: usa el formato «origen destino peso».`);
      (lista[u] ??= []).push([v, peso]);
      lista[v] ??= [];
    });
  if (!Object.keys(lista).length) throw new Error("El grafo está vacío.");
  return lista;
}

function jsonALista(texto) {
  let d;
  try {
    d = JSON.parse(texto);
  } catch {
    throw new Error("El texto no es JSON válido.");
  }
  if (d.lista_adyacencia) return { lista: d.lista_adyacencia, coordenadas: d.coordenadas, dirigido: d.dirigido };
  if (d.aristas) {
    const lista = {};
    d.aristas.forEach(([u, v, w]) => {
      (lista[u] ??= []).push([v, w]);
      lista[v] ??= [];
    });
    return { lista, coordenadas: d.coordenadas, dirigido: d.dirigido };
  }
  if (d.matriz_adyacencia && d.nodos) {
    const lista = Object.fromEntries(
      d.nodos.map((u, i) => [u, d.nodos.flatMap((v, j) => (d.matriz_adyacencia[i][j] ? [[v, d.matriz_adyacencia[i][j]]] : []))])
    );
    return { lista, coordenadas: d.coordenadas, dirigido: d.dirigido };
  }
  // Una lista de adyacencia directa: {"A": [["B", 3]], ...}
  if (Object.values(d).every(Array.isArray)) return { lista: d };
  throw new Error("Usa lista_adyacencia, aristas o matriz_adyacencia (con nodos).");
}

const nodosDe = (lista) => {
  const todos = new Set(Object.keys(lista));
  Object.values(lista).forEach((vs) => vs.forEach(([v]) => todos.add(v)));
  return [...todos];
};

// ---------------------------------------------------------------------------

export default function Modulo2() {
  const [grafo, setGrafo] = useState({ lista: GRAFO_10, coordenadas: COORDENADAS_10, dirigido: true });
  const nodos = useMemo(() => nodosDe(grafo.lista), [grafo.lista]);

  return (
    <>
      <div className="cabecera-modulo">
        <span className="etiqueta">Módulo 2</span>
        <h2>Asistente de logística y optimización</h2>
        <p>
          Describe una red (ciudades y carreteras, por ejemplo) como un grafo ponderado. Elige un
          origen y un destino, o solo un punto de partida para ver hasta dónde se llega, y compara
          lo que encuentra cada algoritmo con exactamente los mismos datos.
        </p>
      </div>
      <EntradaGrafo grafo={grafo} setGrafo={setGrafo} nodos={nodos} />
      <Comparador grafo={grafo} nodos={nodos} />
      <AgenteViajero grafo={grafo} nodos={nodos} />
    </>
  );
}

// ---------------------------------------------------------------------------

function EntradaGrafo({ grafo, setGrafo, nodos }) {
  const [modo, setModo] = useState("aristas");
  const [texto, setTexto] = useState(() => aristasATexto(GRAFO_10));
  const [json, setJson] = useState(() => JSON.stringify({ lista_adyacencia: GRAFO_10, coordenadas: COORDENADAS_10 }, null, 1));
  const [gen, setGen] = useState({ n: 8, densidad: 0.4, semilla: 7, pesos: "aleatorios" });
  const [errorLocal, setErrorLocal] = useState(null);
  const generar = useLlamada();

  const aplicar = (nuevo) => {
    setErrorLocal(null);
    setGrafo((g) => ({ ...g, ...nuevo }));
  };

  const aplicarTexto = () => {
    try {
      aplicar({ lista: textoALista(texto), coordenadas: null });
    } catch (e) {
      setErrorLocal(e.message);
    }
  };

  const aplicarJson = () => {
    try {
      const r = jsonALista(json);
      aplicar({ lista: r.lista, coordenadas: r.coordenadas ?? null, ...(r.dirigido !== undefined && { dirigido: r.dirigido }) });
    } catch (e) {
      setErrorLocal(e.message);
    }
  };

  const generarGrafo = async (e) => {
    e.preventDefault();
    const r = await generar.ejecutar(() =>
      post("/graph/generate", {
        n: Number(gen.n),
        densidad: Number(gen.densidad),
        semilla: gen.semilla === "" ? null : Number(gen.semilla),
        pesos: gen.pesos,
        dirigido: false,
      })
    );
    if (r) {
      aplicar({ lista: r.lista_adyacencia, coordenadas: r.coordenadas, dirigido: false });
      setTexto(aristasATexto(r.lista_adyacencia));
    }
  };

  const restaurar = () => {
    aplicar({ lista: GRAFO_10, coordenadas: COORDENADAS_10, dirigido: true });
    setTexto(aristasATexto(GRAFO_10));
  };

  const numAristas = Object.values(grafo.lista).reduce((s, vs) => s + vs.length, 0);

  return (
    <div className="dos-columnas">
      <div className="panel">
        <h3>1. Describe el grafo</h3>
        <div style={{ marginBottom: "0.9rem" }}>
          <Segmentado
            etiqueta="Forma de capturar el grafo"
            valor={modo}
            onChange={setModo}
            opciones={[
              { valor: "aristas", texto: "Aristas" },
              { valor: "json", texto: "JSON" },
              { valor: "generar", texto: "Generar al azar" },
            ]}
          />
        </div>

        {modo === "aristas" && (
          <>
            <label className="campo">
              Una arista por línea: origen destino peso
              <span className="ayuda">Ejemplo: «A B 15». Al aplicar se pierden las coordenadas (se dibuja en círculo).</span>
              <textarea rows={9} value={texto} onChange={(e) => setTexto(e.target.value)} />
            </label>
            <div className="fila" style={{ marginTop: "0.6rem" }}>
              <button type="button" className="btn primario" onClick={aplicarTexto}>Aplicar</button>
              <button type="button" className="btn" onClick={restaurar}>Grafo de ejemplo (10 nodos)</button>
            </div>
          </>
        )}

        {modo === "json" && (
          <>
            <label className="campo">
              lista_adyacencia, aristas o matriz_adyacencia + nodos (y coordenadas opcionales)
              <textarea rows={9} value={json} onChange={(e) => setJson(e.target.value)} />
            </label>
            <div className="fila" style={{ marginTop: "0.6rem" }}>
              <button type="button" className="btn primario" onClick={aplicarJson}>Aplicar</button>
            </div>
          </>
        )}

        {modo === "generar" && (
          <form onSubmit={generarGrafo}>
            <div className="rejilla">
              <label className="campo">Nodos (n)<input type="number" min="2" max="60" value={gen.n} onChange={(e) => setGen({ ...gen, n: e.target.value })} /></label>
              <label className="campo">Densidad (0–1)<input type="number" min="0" max="1" step="0.05" value={gen.densidad} onChange={(e) => setGen({ ...gen, densidad: e.target.value })} /></label>
              <label className="campo">Semilla<input type="number" value={gen.semilla} onChange={(e) => setGen({ ...gen, semilla: e.target.value })} /></label>
              <label className="campo">
                Pesos
                <select value={gen.pesos} onChange={(e) => setGen({ ...gen, pesos: e.target.value })}>
                  <option value="aleatorios">Aleatorios</option>
                  <option value="euclidianos">Distancia euclidiana</option>
                </select>
              </label>
            </div>
            <p className="suave" style={{ marginTop: "0.6rem" }}>
              Siempre es conexo: incluye un ciclo que pasa por todos los nodos. Se genera sin dirección.
            </p>
            <BotonEnviar cargando={generar.cargando}>Generar grafo</BotonEnviar>
            <ErrorMsg error={generar.error} />
          </form>
        )}

        <label className="fila" style={{ marginTop: "0.9rem", gap: "0.4rem", alignItems: "center" }}>
          <input type="checkbox" checked={grafo.dirigido} onChange={(e) => setGrafo({ ...grafo, dirigido: e.target.checked })} />
          Grafo dirigido (si no, cada arista se recorre en ambos sentidos)
        </label>
        <ErrorMsg error={errorLocal} />
      </div>

      <div className="panel">
        <h3>Vista previa</h3>
        <GrafoSVG lista={grafo.lista} coordenadas={grafo.coordenadas} dirigido={grafo.dirigido} />
        <p className="suave" style={{ marginTop: "0.5rem", marginBottom: 0 }}>
          {nodos.length} nodos · {numAristas} aristas · {grafo.dirigido ? "dirigido" : "no dirigido"} ·{" "}
          {grafo.coordenadas ? "con coordenadas" : "sin coordenadas"}
        </p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

function Comparador({ grafo, nodos }) {
  const [tarea, setTarea] = useState("ruta");
  const [origen, setOrigen] = useState("A");
  const [destino, setDestino] = useState("J");
  const [heuristica, setHeuristica] = useState("euclidiana");
  const [algoritmos, setAlgoritmos] = useState(ALGORITMOS_RUTA.map((a) => a.clave));
  const [seleccion, setSeleccion] = useState(null);
  const { cargando, error, datos, ejecutar } = useLlamada();

  const o = nodos.includes(origen) ? origen : nodos[0];
  const d = nodos.includes(destino) ? destino : nodos[nodos.length - 1];
  const h = grafo.coordenadas ? heuristica : "saltos";
  const disponibles = tarea === "alcance" ? algoritmos.filter((a) => a === "bfs" || a === "dfs") : algoritmos;

  const alternar = (clave) =>
    setAlgoritmos((as) => (as.includes(clave) ? as.filter((x) => x !== clave) : [...as, clave]));

  const enviar = async (e) => {
    e.preventDefault();
    const base = { lista_adyacencia: grafo.lista, dirigido: grafo.dirigido, origen: o };
    const r = await ejecutar(async () => {
      if (!disponibles.length) throw new Error("Elige al menos un algoritmo.");
      if (tarea === "ruta") {
        const res = await post("/graph/compare", {
          ...base,
          destino: d,
          heuristica: h,
          ...(h === "euclidiana" && { coordenadas: grafo.coordenadas }),
          algoritmos: disponibles,
        });
        return { tarea, ...res, snapshot: grafo };
      }
      // Alcance máximo: cada recorrido por separado, porque traen el nivel de cada nodo.
      const filas = await Promise.all(
        disponibles.map(async (clave) => ({ clave, ...(await post(`/graph/${clave}`, base)) }))
      );
      return { tarea, tabla: filas, origen: o, snapshot: grafo };
    });
    if (r) setSeleccion(r.mejor ?? r.tabla[0]?.clave ?? null);
  };

  const fila = datos?.tabla.find((f) => f.clave === seleccion) ?? datos?.tabla[0];

  return (
    <>
      <form className="panel" onSubmit={enviar}>
        <h3>2. Elige la tarea y los algoritmos</h3>
        <div className="fila" style={{ marginBottom: "1rem" }}>
          <Segmentado
            etiqueta="Tarea"
            valor={tarea}
            onChange={setTarea}
            opciones={[
              { valor: "ruta", texto: "Ruta de origen a destino" },
              { valor: "alcance", texto: "Alcance máximo desde un punto" },
            ]}
          />
        </div>
        <div className="rejilla" style={{ marginBottom: "1rem" }}>
          <label className="campo">
            Origen
            <select value={o} onChange={(e) => setOrigen(e.target.value)}>
              {nodos.map((n) => <option key={n}>{n}</option>)}
            </select>
          </label>
          {tarea === "ruta" && (
            <>
              <label className="campo">
                Destino
                <select value={d} onChange={(e) => setDestino(e.target.value)}>
                  {nodos.map((n) => <option key={n}>{n}</option>)}
                </select>
              </label>
              <label className="campo">
                Heurística h(n)
                <span className="ayuda">La usan Hill-Climbing, voraz y A*.</span>
                <select value={h} onChange={(e) => setHeuristica(e.target.value)}>
                  <option value="euclidiana" disabled={!grafo.coordenadas}>
                    Distancia euclidiana{grafo.coordenadas ? "" : " (requiere coordenadas)"}
                  </option>
                  <option value="saltos">Saltos al destino × peso mínimo</option>
                </select>
              </label>
            </>
          )}
        </div>
        <div className="opciones">
          {ALGORITMOS_RUTA.map((a) => {
            const deshabilitado = tarea === "alcance" && !a.sinDestino;
            return (
              <label className="opcion" key={a.clave}>
                <input
                  type="checkbox"
                  checked={algoritmos.includes(a.clave) && !deshabilitado}
                  disabled={deshabilitado}
                  onChange={() => alternar(a.clave)}
                />
                <span>
                  <strong><span className="punto" style={{ background: COLORES[a.clave] }} />{a.nombre}</strong>
                  <small>{deshabilitado ? "Necesita un destino" : a.nota}</small>
                </span>
              </label>
            );
          })}
        </div>
        <div style={{ marginTop: "1rem" }}>
          <BotonEnviar cargando={cargando}>{tarea === "ruta" ? "Comparar rutas" : "Calcular alcance"}</BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      {datos && fila && (
        <div className="panel">
          <h3>
            3. Resultados{" "}
            {datos.tarea === "ruta" ? `de ${datos.origen} a ${datos.destino}` : `· alcance desde ${datos.origen}`}
          </h3>
          <div className="dos-columnas">
            <div>
              <GrafoSVG
                lista={datos.snapshot.lista}
                coordenadas={datos.snapshot.coordenadas}
                dirigido={datos.snapshot.dirigido}
                ruta={fila.ruta}
                orden={fila.orden_visita ?? []}
                niveles={fila.alcance}
              />
              <div className="leyenda">
                <span><span className="punto" style={{ background: COLORES[fila.clave] }} />Mostrando: {fila.algoritmo}</span>
                <span>Los números junto a cada nodo son el orden de visita.</span>
                {fila.alcance && <span>Color del nodo = nivel (frío = cerca, cálido = lejos).</span>}
              </div>
            </div>
            <div>
              <p className="suave">Haz clic en una fila para ver su ruta en el grafo.</p>
              <div className="tabla-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Algoritmo</th>
                      {datos.tarea === "ruta" ? <th>Ruta</th> : <th>Alcanzados</th>}
                      {datos.tarea === "ruta" && <th className="num">Costo</th>}
                      <th className="num">Nodos</th>
                      <th className="num">ms</th>
                      <th className="num">KB</th>
                    </tr>
                  </thead>
                  <tbody>
                    {datos.tabla.map((f) => (
                      <tr
                        key={f.clave}
                        className={`seleccionable ${f.clave === fila.clave ? "seleccionada" : ""}`}
                        onClick={() => setSeleccion(f.clave)}
                        tabIndex={0}
                        onKeyDown={(e) => e.key === "Enter" && setSeleccion(f.clave)}
                      >
                        <td>
                          <span className="punto" style={{ background: COLORES[f.clave] }} />
                          {f.algoritmo}
                          {datos.mejor === f.clave && <> <span className="insignia ok">mejor costo</span></>}
                          {datos.mas_rapido === f.clave && <> <span className="insignia neutra">más rápido</span></>}
                        </td>
                        {datos.tarea === "ruta" ? (
                          <td className="mono">{f.solucion ? f.ruta.join("→") : <span className="insignia mal">sin ruta</span>}</td>
                        ) : (
                          <td className="num">{Object.keys(f.alcance).length}</td>
                        )}
                        {datos.tarea === "ruta" && <td className="num">{fmt(f.costo)}</td>}
                        <td className="num">{f.nodos_recorridos}</td>
                        <td className="num">{fmt(f.tiempo_ms)}</td>
                        <td className="num">{fmt(f.memoria_kb, 2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="suave" style={{ marginTop: "0.75rem" }}>
                <strong>{fila.algoritmo}</strong> · {fila.clase} · {fila.complejidad}
                <br />
                {fila.motivo}
              </p>
              {datos.heuristica && (
                <p className="suave mono">Heurística: {datos.heuristica.formula}</p>
              )}
            </div>
          </div>
          <Explicacion
            texto={datos.explicacion ?? fila.explicacion}
            ia={datos.explicacion_ia ?? fila.explicacion_ia}
          />
        </div>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------

function AgenteViajero({ grafo, nodos }) {
  const [origen, setOrigen] = useState("A");
  const { cargando, error, datos, ejecutar } = useLlamada();
  const o = nodos.includes(origen) ? origen : nodos[0];

  const enviar = (e) => {
    e.preventDefault();
    const cuerpo = { lista_adyacencia: grafo.lista, dirigido: grafo.dirigido, origen: o };
    ejecutar(async () => {
      const [exacto, voraz] = await Promise.allSettled([post("/graph/tsp", cuerpo), post("/graph/tsp/greedy", cuerpo)]);
      return { exacto, voraz, snapshot: grafo };
    });
  };

  return (
    <form className="panel" onSubmit={enviar}>
      <h3>Agente viajero: P contra NP</h3>
      <p className="suave">
        Visitar todos los nodos una sola vez y regresar al inicio con el menor costo es un problema
        NP-difícil. Compara la solución exacta (Held-Karp, tiempo exponencial, hasta 18 nodos) con la
        heurística voraz del vecino más cercano (polinomial, sin garantía de ser la óptima). Los
        grafos generados al azar siempre tienen solución.
      </p>
      <div className="fila">
        <label className="campo">
          Nodo de inicio
          <select value={o} onChange={(e) => setOrigen(e.target.value)}>
            {nodos.map((n) => <option key={n}>{n}</option>)}
          </select>
        </label>
        <BotonEnviar cargando={cargando}>Resolver con ambos</BotonEnviar>
      </div>
      <ErrorMsg error={error} />
      {datos && (
        <div className="dos-columnas" style={{ marginTop: "1rem" }}>
          {[["Exacto (Held-Karp)", datos.exacto], ["Heurística voraz", datos.voraz]].map(([titulo, r]) => (
            <div key={titulo}>
              <h4>{titulo}</h4>
              {r.status === "rejected" ? (
                <ErrorMsg error={r.reason.message} />
              ) : (
                <>
                  <GrafoSVG
                    lista={datos.snapshot.lista}
                    coordenadas={datos.snapshot.coordenadas}
                    dirigido={datos.snapshot.dirigido}
                    ruta={r.value.ruta}
                  />
                  <p style={{ marginTop: "0.5rem" }}>
                    {r.value.solucion ? (
                      <>
                        <span className="insignia ok">Costo {fmt(r.value.costo)}</span>{" "}
                        <span className="mono">{r.value.ruta.join("→")}</span>
                      </>
                    ) : (
                      <span className="insignia mal">Sin ciclo</span>
                    )}
                  </p>
                  <p className="suave">
                    {r.value.clase} · {r.value.complejidad} · {fmt(r.value.tiempo_ms)} ms ·{" "}
                    {fmt(r.value.memoria_kb, 2)} KB · {r.value.operaciones} operaciones
                  </p>
                  <Explicacion texto={r.value.explicacion} ia={r.value.explicacion_ia} />
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </form>
  );
}
