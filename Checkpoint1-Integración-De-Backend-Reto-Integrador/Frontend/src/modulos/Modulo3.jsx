import { useState } from "react";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  LogarithmicScale,
  PointElement,
  Tooltip,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";
import { post, postArchivo } from "../api.js";
import { ALGORITMOS_ORDEN, COLORES } from "../datos.js";
import { useLlamada } from "../useLlamada.js";
import BotonEnviar from "../components/BotonEnviar.jsx";
import ErrorMsg from "../components/ErrorMsg.jsx";
import Explicacion from "../components/Explicacion.jsx";
import ListaInput from "../components/ListaInput.jsx";
import Segmentado from "../components/Segmentado.jsx";

ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, LineElement, LogarithmicScale, PointElement, Tooltip);

const fmt = (x, d = 4) => Number(Number(x).toFixed(d)).toLocaleString("es-MX");
const nombreDe = (clave) => ALGORITMOS_ORDEN.find((a) => a.clave === clave)?.nombre ?? clave;

// Colores de texto y rejilla de Chart.js según el tema del sistema.
function colorEjes() {
  const estilos = getComputedStyle(document.documentElement);
  return { texto: estilos.getPropertyValue("--texto-suave").trim(), rejilla: estilos.getPropertyValue("--borde").trim() };
}

export default function Modulo3() {
  const [vista, setVista] = useState("ordenamiento");
  return (
    <>
      <div className="cabecera-modulo">
        <span className="etiqueta">Módulo 3</span>
        <h2>Auditoría de escalabilidad y benchmark de algoritmos</h2>
        <p>
          Dos algoritmos pueden resolver el mismo problema con costos muy distintos. Ordena los
          mismos datos con varios algoritmos, mide su tiempo y memoria, y observa cómo crece el
          costo cuando aumenta el tamaño de la entrada.
        </p>
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <Segmentado
          etiqueta="Herramienta"
          valor={vista}
          onChange={setVista}
          opciones={[
            { valor: "ordenamiento", texto: "Comparar ordenamientos" },
            { valor: "escalabilidad", texto: "Escalabilidad (gráfica vs n)" },
            { valor: "complejidad", texto: "Analizador de complejidad" },
          ]}
        />
      </div>
      <div hidden={vista !== "ordenamiento"}><Ordenamiento /></div>
      <div hidden={vista !== "escalabilidad"}><Escalabilidad /></div>
      <div hidden={vista !== "complejidad"}><Complejidad /></div>
    </>
  );
}

function SelectorAlgoritmos({ seleccion, setSeleccion, n }) {
  const alternar = (clave) =>
    setSeleccion((s) => (s.includes(clave) ? s.filter((x) => x !== clave) : [...s, clave]));
  return (
    <div className="opciones">
      {ALGORITMOS_ORDEN.map((a) => {
        const excede = n !== undefined && n > a.max;
        return (
          <label className="opcion" key={a.clave}>
            <input type="checkbox" checked={seleccion.includes(a.clave)} onChange={() => alternar(a.clave)} />
            <span>
              <strong><span className="punto" style={{ background: COLORES[a.clave] }} />{a.nombre}</strong>
              <small style={excede && seleccion.includes(a.clave) ? { color: "var(--mal)" } : undefined}>
                {a.complejidad} · hasta {a.max.toLocaleString("es-MX")}
              </small>
            </span>
          </label>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------

function Ordenamiento() {
  const [seleccion, setSeleccion] = useState(["burbuja", "insercion", "merge", "quick"]);
  const [origen, setOrigen] = useState("generar");
  const [datosPropios, setDatosPropios] = useState([5, 3, 8, 1, 9, 2, 7, 4]);
  const [n, setN] = useState(1000);
  const [distribucion, setDistribucion] = useState("aleatoria");
  const [semilla, setSemilla] = useState(1);
  const [metrica, setMetrica] = useState("tiempo_ms");
  const { cargando, error, datos, ejecutar } = useLlamada();

  const tamano = origen === "generar" ? Number(n) : datosPropios.length;

  const enviar = (e) => {
    e.preventDefault();
    const cuerpo =
      origen === "generar"
        ? { algoritmos: seleccion, n: Number(n), distribucion, semilla: semilla === "" ? null : Number(semilla) }
        : { algoritmos: seleccion, datos: datosPropios };
    ejecutar(() => post("/benchmark/ordenamiento", cuerpo));
  };

  const ejes = colorEjes();
  const ETIQUETAS = { tiempo_ms: "Tiempo (ms)", memoria_kb: "Memoria (KB)", comparaciones: "Comparaciones" };

  return (
    <>
      <form className="panel" onSubmit={enviar}>
        <h3>1. Elige al menos 2 algoritmos</h3>
        <SelectorAlgoritmos seleccion={seleccion} setSeleccion={setSeleccion} n={tamano} />

        <h3 style={{ marginTop: "1.25rem" }}>2. Datos a ordenar</h3>
        <div style={{ marginBottom: "0.9rem" }}>
          <Segmentado
            etiqueta="Origen de los datos"
            valor={origen}
            onChange={setOrigen}
            opciones={[
              { valor: "generar", texto: "Generar lista" },
              { valor: "propia", texto: "Escribir mi lista" },
            ]}
          />
        </div>
        {origen === "generar" ? (
          <div className="rejilla">
            <label className="campo">Tamaño n<input type="number" min="1" max="50000" value={n} onChange={(e) => setN(e.target.value)} /></label>
            <label className="campo">
              Distribución
              <select value={distribucion} onChange={(e) => setDistribucion(e.target.value)}>
                <option value="aleatoria">Aleatoria (caso promedio)</option>
                <option value="ordenada">Ya ordenada (mejor caso)</option>
                <option value="inversa">Orden inverso (peor caso)</option>
                <option value="casi_ordenada">Casi ordenada</option>
              </select>
            </label>
            <label className="campo">Semilla<input type="number" value={semilla} onChange={(e) => setSemilla(e.target.value)} /></label>
          </div>
        ) : (
          <label className="campo">
            Números (Enter o coma para agregar)
            <ListaInput valores={datosPropios} onChange={setDatosPropios} numerica permitirVacia={false} etiqueta="Números a ordenar" />
          </label>
        )}
        <div style={{ marginTop: "1rem" }}>
          <BotonEnviar cargando={cargando} disabled={cargando || seleccion.length < 2}>
            {seleccion.length < 2 ? "Elige al menos 2 algoritmos" : "Ordenar y comparar"}
          </BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      {datos && (
        <div className="panel">
          <h3>3. Resultados · n = {datos.n.toLocaleString("es-MX")} ({datos.distribucion})</h3>
          <p className="suave" style={{ marginBottom: "0.3rem" }}>Lista ordenada{datos.datos_ordenados.length > 40 ? " (primeros 40)" : ""}:</p>
          <p className="mono" style={{ wordBreak: "break-word" }}>
            [{datos.datos_ordenados.slice(0, 40).join(", ")}{datos.datos_ordenados.length > 40 ? ", …" : ""}]
          </p>

          <div className="tabla-scroll" style={{ marginBottom: "1rem" }}>
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Algoritmo</th>
                  <th className="num">Tiempo (ms)</th>
                  <th className="num">Memoria (KB)</th>
                  <th className="num">Comparaciones</th>
                  <th className="num">Intercambios</th>
                  <th>Mejor · Prom. · Peor</th>
                  <th>Espacio</th>
                  <th>Clase</th>
                  <th>Correcto</th>
                </tr>
              </thead>
              <tbody>
                {datos.ranking.map((clave, i) => {
                  const r = datos.resultados.find((x) => x.clave === clave);
                  return (
                    <tr key={clave} title={r.explicacion}>
                      <td>{i + 1}</td>
                      <td><span className="punto" style={{ background: COLORES[clave] }} />{nombreDe(clave)}</td>
                      <td className="num">{fmt(r.tiempo_ms)}</td>
                      <td className="num">{fmt(r.memoria_kb, 2)}</td>
                      <td className="num">{r.comparaciones.toLocaleString("es-MX")}</td>
                      <td className="num">{r.intercambios.toLocaleString("es-MX")}</td>
                      <td className="mono">{r.complejidad.mejor} · {r.complejidad.promedio} · {r.complejidad.peor}</td>
                      <td>{r.espacio}</td>
                      <td>{r.clase}</td>
                      <td>{r.correcto ? <span className="insignia ok">✓</span> : <span className="insignia mal">✗</span>}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="fila" style={{ justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <h4 style={{ margin: 0 }}>Gráfica comparativa</h4>
            <Segmentado
              etiqueta="Métrica de la gráfica"
              valor={metrica}
              onChange={setMetrica}
              opciones={Object.entries(ETIQUETAS).map(([valor, texto]) => ({ valor, texto }))}
            />
          </div>
          <div className="grafica">
            <Bar
              data={{
                labels: datos.ranking.map(nombreDe),
                datasets: [
                  {
                    label: ETIQUETAS[metrica],
                    data: datos.ranking.map((c) => datos.resultados.find((r) => r.clave === c)[metrica]),
                    backgroundColor: datos.ranking.map((c) => COLORES[c]),
                    borderRadius: 6,
                  },
                ],
              }}
              options={{
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: ejes.texto }, grid: { display: false } },
                  y: { ticks: { color: ejes.texto }, grid: { color: ejes.rejilla }, title: { display: true, text: ETIQUETAS[metrica], color: ejes.texto } },
                },
              }}
            />
          </div>

          <h4 style={{ marginTop: "1rem" }}>Cómo funciona cada uno</h4>
          <ul className="suave">
            {datos.resultados.map((r) => (
              <li key={r.clave}><strong>{nombreDe(r.clave)}:</strong> {r.explicacion}</li>
            ))}
          </ul>
          <Explicacion texto={datos.explicacion} />
        </div>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------

function Escalabilidad() {
  const [seleccion, setSeleccion] = useState(["burbuja", "insercion", "merge", "quick", "heap"]);
  const [tamanos, setTamanos] = useState([100, 500, 1000, 2000]);
  const [distribucion, setDistribucion] = useState("aleatoria");
  const [log, setLog] = useState(false);
  const { cargando, error, datos, ejecutar } = useLlamada();

  const enviar = (e) => {
    e.preventDefault();
    ejecutar(() => post("/benchmark/escalabilidad", { algoritmos: seleccion, tamanos, distribucion }));
  };

  const ejes = colorEjes();

  return (
    <>
      <form className="panel" onSubmit={enviar}>
        <h3>1. Algoritmos a medir</h3>
        <SelectorAlgoritmos seleccion={seleccion} setSeleccion={setSeleccion} n={Math.max(0, ...tamanos)} />
        <div className="rejilla" style={{ marginTop: "1rem" }}>
          <label className="campo">
            Tamaños n a probar
            <span className="ayuda">De 2 a 10 tamaños (Enter o coma para agregar).</span>
            <ListaInput valores={tamanos} onChange={(v) => setTamanos(v.map((x) => Math.round(x)).filter((x) => x > 0))} numerica permitirVacia={false} etiqueta="Tamaños" />
          </label>
          <label className="campo">
            Distribución
            <select value={distribucion} onChange={(e) => setDistribucion(e.target.value)}>
              <option value="aleatoria">Aleatoria</option>
              <option value="ordenada">Ya ordenada</option>
              <option value="inversa">Orden inverso</option>
              <option value="casi_ordenada">Casi ordenada</option>
            </select>
          </label>
        </div>
        <div style={{ marginTop: "1rem" }}>
          <BotonEnviar cargando={cargando} disabled={cargando || seleccion.length < 2}>
            {seleccion.length < 2 ? "Elige al menos 2 algoritmos" : "Medir crecimiento"}
          </BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      {datos && (
        <div className="panel">
          <div className="fila" style={{ justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <h3 style={{ margin: 0 }}>Tiempo contra n</h3>
            <label className="fila" style={{ gap: "0.4rem", alignItems: "center" }}>
              <input type="checkbox" checked={log} onChange={(e) => setLog(e.target.checked)} />
              Escala logarítmica
            </label>
          </div>
          <div className="grafica" style={{ height: 380 }}>
            <Line
              data={{
                datasets: Object.entries(datos.series).map(([clave, puntos]) => ({
                  label: nombreDe(clave),
                  data: puntos.map((p) => ({ x: p.n, y: Math.max(p.tiempo_ms, 0.0001) })),
                  borderColor: COLORES[clave],
                  backgroundColor: COLORES[clave],
                  tension: 0.25,
                })),
              }}
              options={{
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: { legend: { labels: { color: ejes.texto } } },
                scales: {
                  x: {
                    type: "linear",
                    title: { display: true, text: "n (tamaño de la lista)", color: ejes.texto },
                    ticks: { color: ejes.texto },
                    grid: { color: ejes.rejilla },
                  },
                  y: {
                    type: log ? "logarithmic" : "linear",
                    title: { display: true, text: "Tiempo (ms)", color: ejes.texto },
                    ticks: { color: ejes.texto },
                    grid: { color: ejes.rejilla },
                  },
                },
              }}
            />
          </div>
          <div className="tabla-scroll" style={{ marginTop: "1rem" }}>
            <table>
              <thead>
                <tr>
                  <th>Algoritmo</th>
                  <th>Teórico</th>
                  {datos.tamanos.map((t) => <th className="num" key={t}>n = {t.toLocaleString("es-MX")}</th>)}
                </tr>
              </thead>
              <tbody>
                {datos.algoritmos.map((a) => (
                  <tr key={a.clave}>
                    <td><span className="punto" style={{ background: COLORES[a.clave] }} />{nombreDe(a.clave)}</td>
                    <td className="mono">{a.complejidad.promedio}</td>
                    {datos.series[a.clave].map((p) => <td className="num" key={p.n}>{fmt(p.tiempo_ms)} ms</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Explicacion texto={datos.explicacion} />
        </div>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------

function Complejidad() {
  const [archivo, setArchivo] = useState(null);
  const [caso, setCaso] = useState("peor");
  const { cargando, error, datos, ejecutar } = useLlamada();

  const enviar = (e) => {
    e.preventDefault();
    ejecutar(async () => {
      if (!archivo) throw new Error("Selecciona un archivo .py.");
      return { caso, ...(await postArchivo(`/complejidad/${caso}-caso?formato=json`, archivo)) };
    });
  };

  const descargar = () => {
    const base = (datos.archivo || "programa").replace(/\.[^.]*$/, "").replace(/[^A-Za-z0-9_-]/g, "_");
    const url = URL.createObjectURL(new Blob([datos.archivo_anotado], { type: "text/x-python" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `${base}_${datos.caso}_caso.py`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <form className="panel" onSubmit={enviar}>
        <h3>Analiza la complejidad de tu programa</h3>
        <p className="suave">
          Sube un programa en Python. Se anota cada línea con su costo y se suman para obtener la
          complejidad de cada función y del programa completo.
        </p>
        <div className="fila">
          <label className="campo">
            Archivo .py
            <input type="file" accept=".py,text/x-python" onChange={(e) => setArchivo(e.target.files[0] ?? null)} />
          </label>
          <Segmentado
            etiqueta="Caso"
            valor={caso}
            onChange={setCaso}
            opciones={[
              { valor: "peor", texto: "Peor caso (Big-O)" },
              { valor: "mejor", texto: "Mejor caso (Big-Ω)" },
            ]}
          />
          <BotonEnviar cargando={cargando}>Analizar</BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      {datos && (
        <div className="panel">
          <div className="fila" style={{ justifyContent: "space-between" }}>
            <h3 style={{ margin: 0 }}>
              {datos.archivo}: <span className="mono">{datos.programa.complejidad}</span>
            </h3>
            <button type="button" className="btn" onClick={descargar}>Descargar archivo anotado</button>
          </div>
          <div className="tabla-scroll" style={{ margin: "1rem 0" }}>
            <table>
              <thead>
                <tr>
                  <th>Función</th>
                  <th>Complejidad</th>
                  <th>Suma de líneas</th>
                  <th>Recurrencia</th>
                </tr>
              </thead>
              <tbody>
                {datos.funciones.map((f) => (
                  <tr key={`${f.nombre}-${f.linea}`}>
                    <td className="mono">{f.nombre}</td>
                    <td className="mono"><strong>{f.complejidad}</strong></td>
                    <td className="mono">{f.suma_agrupada}</td>
                    <td className="mono">{f.recurrencia ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Explicacion texto={datos.explicacion} />
          <h4 style={{ marginTop: "1rem" }}>Código anotado</h4>
          <pre className="codigo">{datos.archivo_anotado}</pre>
        </div>
      )}
    </>
  );
}
