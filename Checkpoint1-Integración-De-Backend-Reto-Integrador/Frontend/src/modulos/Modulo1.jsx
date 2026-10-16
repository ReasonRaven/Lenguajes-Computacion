import { useState } from "react";
import { post } from "../api.js";
import { EJEMPLOS_AUTOMATAS } from "../datos.js";
import { useLlamada } from "../useLlamada.js";
import BotonEnviar from "../components/BotonEnviar.jsx";
import ErrorMsg from "../components/ErrorMsg.jsx";
import Explicacion from "../components/Explicacion.jsx";
import ListaInput, { Conjunto, mostrar } from "../components/ListaInput.jsx";
import Segmentado from "../components/Segmentado.jsx";
import TablaTransiciones, { automataDesdeEjemplo, tablaParaApi } from "../components/TablaTransiciones.jsx";

export default function Modulo1() {
  const [vista, setVista] = useState("automatas");
  return (
    <>
      <div className="cabecera-modulo">
        <span className="etiqueta">Módulo 1</span>
        <h2>Traductor de lenguajes y verificador de reglas</h2>
        <p>
          Una cadena es una secuencia finita de símbolos y un lenguaje es un conjunto de cadenas.
          Aquí puedes operar con ellos y comprobar si una palabra pertenece al lenguaje de un
          autómata finito.
        </p>
      </div>
      <div style={{ marginBottom: "1rem" }}>
        <Segmentado
          etiqueta="Herramienta"
          valor={vista}
          onChange={setVista}
          opciones={[
            { valor: "automatas", texto: "Autómatas (AFD · AFND · AFND-ε)" },
            { valor: "cadenas", texto: "Cadenas" },
            { valor: "lenguajes", texto: "Lenguajes" },
          ]}
        />
      </div>
      <div hidden={vista !== "automatas"}><Automatas /></div>
      <div hidden={vista !== "cadenas"}><Cadenas /></div>
      <div hidden={vista !== "lenguajes"}><Lenguajes /></div>
    </>
  );
}

// ---------------------------------------------------------------------------

function Cadenas() {
  const [op, setOp] = useState("concatenar");
  const [a, setA] = useState("ab");
  const [b, setB] = useState("ba");
  const [lista, setLista] = useState(["ab", "c", "ab"]);
  const [cadena, setCadena] = useState("ab");
  const [n, setN] = useState(3);
  const { cargando, error, datos, ejecutar, setDatos } = useLlamada();

  const enviar = (e) => {
    e.preventDefault();
    const cuerpo =
      op === "concatenar" ? { a, b } : op === "unir" ? { cadenas: lista } : { cadena, n: Number(n) };
    ejecutar(() => post(`/cadenas/${op}`, cuerpo));
  };

  return (
    <div className="dos-columnas">
      <form className="panel" onSubmit={enviar}>
        <h3>Operación con cadenas</h3>
        <div style={{ marginBottom: "1rem" }}>
          <Segmentado
            etiqueta="Operación"
            valor={op}
            onChange={(v) => { setOp(v); setDatos(null); }}
            opciones={[
              { valor: "concatenar", texto: "w · v" },
              { valor: "unir", texto: "w₁w₂…wₙ" },
              { valor: "potencia", texto: "wⁿ" },
            ]}
          />
        </div>
        {op === "concatenar" && (
          <div className="rejilla">
            <label className="campo">Cadena w<input type="text" value={a} onChange={(e) => setA(e.target.value)} /></label>
            <label className="campo">Cadena v<input type="text" value={b} onChange={(e) => setB(e.target.value)} /></label>
          </div>
        )}
        {op === "unir" && (
          <label className="campo">
            Cadenas a concatenar, en orden
            <span className="ayuda">Enter o coma para agregar; Enter con el campo vacío agrega λ.</span>
            <ListaInput valores={lista} onChange={setLista} etiqueta="Cadenas" />
          </label>
        )}
        {op === "potencia" && (
          <div className="rejilla">
            <label className="campo">Cadena w<input type="text" value={cadena} onChange={(e) => setCadena(e.target.value)} /></label>
            <label className="campo">Exponente n<input type="number" min="0" max="1000" value={n} onChange={(e) => setN(e.target.value)} /></label>
          </div>
        )}
        <div style={{ marginTop: "1rem" }}>
          <BotonEnviar cargando={cargando}>Calcular</BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      <div className="panel">
        <h3>Resultado</h3>
        {datos ? (
          <>
            <div className="resultado-grande">{mostrar(datos.resultado)}</div>
            <p className="suave">Longitud: {datos.resultado.length}</p>
            <Explicacion texto={datos.explicacion} />
          </>
        ) : (
          <p className="suave">Elige una operación y presiona «Calcular».</p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

const OPS_LENGUAJE = [
  { valor: "union", texto: "L ∪ M" },
  { valor: "interseccion", texto: "L ∩ M" },
  { valor: "diferencia", texto: "L − M" },
  { valor: "concatenacion", texto: "LM" },
  { valor: "complemento", texto: "L̄" },
  { valor: "clausura_kleene", texto: "L*" },
];

function Lenguajes() {
  const [op, setOp] = useState("union");
  const [L, setL] = useState(["a", "ab", "b"]);
  const [M, setM] = useState(["b", "ba", ""]);
  const [alfabeto, setAlfabeto] = useState(["a", "b"]);
  const [maxLength, setMaxLength] = useState(2);
  const [maxElementos, setMaxElementos] = useState(10);
  const { cargando, error, datos, ejecutar, setDatos } = useLlamada();
  const usaM = ["union", "interseccion", "diferencia", "concatenacion"].includes(op);

  const enviar = (e) => {
    e.preventDefault();
    let cuerpo = { L, M };
    if (op === "complemento") cuerpo = { L, alfabeto, max_length: Number(maxLength) };
    if (op === "clausura_kleene") cuerpo = { L, max_elementos: Number(maxElementos) };
    ejecutar(() => post(`/lenguajes/${op}`, cuerpo));
  };

  return (
    <div className="dos-columnas">
      <form className="panel" onSubmit={enviar}>
        <h3>Operación con lenguajes</h3>
        <div style={{ marginBottom: "1rem" }}>
          <Segmentado etiqueta="Operación" valor={op} onChange={(v) => { setOp(v); setDatos(null); }} opciones={OPS_LENGUAJE} />
        </div>
        <div style={{ display: "grid", gap: "0.9rem" }}>
          <label className="campo">
            Lenguaje L
            <span className="ayuda">Enter o coma para agregar; Enter con el campo vacío agrega λ.</span>
            <ListaInput valores={L} onChange={setL} etiqueta="Lenguaje L" />
          </label>
          {usaM && (
            <label className="campo">
              Lenguaje M
              <ListaInput valores={M} onChange={setM} etiqueta="Lenguaje M" />
            </label>
          )}
          {op === "complemento" && (
            <div className="rejilla">
              <label className="campo">
                Alfabeto Σ
                <ListaInput valores={alfabeto} onChange={setAlfabeto} permitirVacia={false} etiqueta="Alfabeto" />
              </label>
              <label className="campo">
                Longitud máxima
                <span className="ayuda">Σ* es infinito: se acota hasta esta longitud.</span>
                <input type="number" min="0" max="8" value={maxLength} onChange={(e) => setMaxLength(e.target.value)} />
              </label>
            </div>
          )}
          {op === "clausura_kleene" && (
            <label className="campo">
              Cuántos elementos mostrar
              <span className="ayuda">L* es infinito: se listan los primeros en orden por longitud.</span>
              <input type="number" min="1" max="200" value={maxElementos} onChange={(e) => setMaxElementos(e.target.value)} />
            </label>
          )}
        </div>
        <div style={{ marginTop: "1rem" }}>
          <BotonEnviar cargando={cargando}>Calcular</BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      <div className="panel">
        <h3>Resultado</h3>
        {datos ? (
          <>
            <p className="suave">{datos.resultado.length} cadena(s):</p>
            <Conjunto elementos={datos.resultado} />
            <Explicacion texto={datos.explicacion} />
          </>
        ) : (
          <p className="suave">Define los lenguajes y presiona «Calcular».</p>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

const RUTA_AUTOMATA = { AFD: "/afd/evaluar", AFND: "/afnd/evaluar", "AFND-ε": "/afnd-e/evaluar" };

function Automatas() {
  const [tipo, setTipo] = useState("AFD");
  const [automata, setAutomata] = useState(() => automataDesdeEjemplo(EJEMPLOS_AUTOMATAS.AFD));
  const [cadenas, setCadenas] = useState(EJEMPLOS_AUTOMATAS.AFD.cadenas);
  const { cargando, error, datos, ejecutar, setDatos } = useLlamada();

  const cargarEjemplo = (t) => {
    setAutomata(automataDesdeEjemplo(EJEMPLOS_AUTOMATAS[t]));
    setCadenas(EJEMPLOS_AUTOMATAS[t].cadenas);
    setDatos(null);
  };

  const cambiarTipo = (t) => {
    setTipo(t);
    cargarEjemplo(t);
  };

  const enviar = (e) => {
    e.preventDefault();
    const cuerpo = {
      tabla: tablaParaApi(automata, { deterministico: tipo === "AFD", conLambda: tipo === "AFND-ε" }),
      estado_inicial: automata.inicial,
      estados_finales: automata.finales,
      cadenas,
    };
    ejecutar(() => post(RUTA_AUTOMATA[tipo], cuerpo));
  };

  return (
    <>
      <form className="panel" onSubmit={enviar}>
        <div className="fila" style={{ justifyContent: "space-between", marginBottom: "0.75rem" }}>
          <h3 style={{ margin: 0 }}>Define tu autómata</h3>
          <Segmentado etiqueta="Tipo de autómata" valor={tipo} onChange={cambiarTipo} opciones={["AFD", "AFND", "AFND-ε"]} />
        </div>
        <p className="suave">
          Ejemplo cargado: {EJEMPLOS_AUTOMATAS[tipo].descripcion}{" "}
          <button type="button" className="btn chico" onClick={() => cargarEjemplo(tipo)}>
            Restaurar ejemplo
          </button>
        </p>
        <TablaTransiciones
          automata={automata}
          onChange={setAutomata}
          deterministico={tipo === "AFD"}
          conLambda={tipo === "AFND-ε"}
        />
        <label className="campo" style={{ marginTop: "1rem" }}>
          Cadenas a evaluar
          <span className="ayuda">Enter o coma para agregar; Enter con el campo vacío agrega λ (cadena vacía).</span>
          <ListaInput valores={cadenas} onChange={setCadenas} etiqueta="Cadenas a evaluar" />
        </label>
        <div style={{ marginTop: "1rem" }}>
          <BotonEnviar cargando={cargando}>Evaluar cadenas</BotonEnviar>
        </div>
        <ErrorMsg error={error} />
      </form>

      {datos && (
        <div className="panel">
          <h3>
            Resultados · {datos.tipo}{" "}
            <span className="suave mono" style={{ fontWeight: 400 }}>
              Q = {"{"}{datos.estados.join(", ")}{"}"} · Σ = {"{"}{datos.alfabeto.join(", ")}{"}"} · F = {"{"}
              {datos.estados_finales.join(", ")}{"}"}
            </span>
          </h3>
          <div className="tarjetas">
            {datos.resultados.map((r, i) => (
              <article key={i} className={`tarjeta ${r.aceptada ? "ok" : "mal"}`}>
                <header>
                  <span className="cadena">{r.cadena_mostrada}</span>
                  <span className={`insignia ${r.aceptada ? "ok" : "mal"}`}>{r.aceptada ? "Aceptada" : "Rechazada"}</span>
                </header>
                <div className="detalle">{r.notacion}</div>
                {r.camino_aceptacion && <div className="detalle">Camino: {r.camino_aceptacion}</div>}
                <p className="porque">{r.explicacion}</p>
              </article>
            ))}
          </div>
          <Explicacion texto={datos.explicacion} />
        </div>
      )}
    </>
  );
}
