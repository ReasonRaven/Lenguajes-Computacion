import { INTEGRANTES } from "../datos.js";

const MODULOS = [
  {
    id: "modulo1",
    titulo: "1. Traductor de lenguajes y verificador de reglas",
    temas: ["Operaciones con cadenas", "Operaciones con lenguajes", "AFD", "AFND", "AFND-ε"],
    texto: "Escribe cadenas o lenguajes y aplica operaciones, o define un autómata y descubre qué palabras acepta.",
  },
  {
    id: "modulo2",
    titulo: "2. Asistente de logística y optimización",
    temas: ["BFS", "DFS", "Hill-Climbing", "Voraz, A* y Dijkstra", "Agente viajero (P vs NP)"],
    texto: "Describe un grafo, elige origen y destino, y compara las rutas que encuentra cada algoritmo.",
  },
  {
    id: "modulo3",
    titulo: "3. Auditoría de escalabilidad y benchmark",
    temas: ["Algoritmos de ordenamiento", "Clases P, NP y NSPACE", "Crecimiento con n", "Analizador de complejidad"],
    texto: "Ordena los mismos datos con varios algoritmos y mide tiempo y memoria para ver cómo escalan.",
  },
];

export default function Inicio({ ir }) {
  return (
    <>
      <div className="hero">
        <h2>Experimenta con la teoría de la computación</h2>
        <p>
          Una herramienta para estudiantes de nuevo ingreso: prueba autómatas, optimiza rutas y
          compara la complejidad de algoritmos. Cada resultado viene con una explicación del proceso
          y de la teoría que lo sustenta.
        </p>
        <button className="btn primario" onClick={() => ir("modulo1")}>
          Empezar con el módulo 1 →
        </button>
      </div>

      <h3>Módulos del producto</h3>
      <div className="rejilla" style={{ marginBottom: "1.5rem" }}>
        {MODULOS.map((m) => (
          <article className="modulo-card" key={m.id}>
            <h4>{m.titulo}</h4>
            <p style={{ margin: 0, fontSize: "0.92rem" }}>{m.texto}</p>
            <ul>
              {m.temas.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
            <button className="btn" onClick={() => ir(m.id)}>
              Abrir
            </button>
          </article>
        ))}
      </div>

      <h3>Arquitectura del producto</h3>
      <div className="rejilla" style={{ marginBottom: "1.5rem" }}>
        <div className="capa backend">
          <h4>Cómputo determinista (backend)</h4>
          <p>FastAPI con los algoritmos de las actividades 3, 6, 11, 12 y 13, más BFS, DFS, Hill-Climbing y el benchmark.</p>
        </div>
        <div className="capa interpretacion">
          <h4>Capa de interpretación y explicabilidad</h4>
          <p>Cada respuesta incluye una explicación: qué pasó con tus datos y la base teórica.</p>
        </div>
        <div className="capa frontend">
          <h4>Interfaz gráfica (frontend)</h4>
          <p>Esta aplicación en React: formularios, grafos, tablas comparativas y gráficas.</p>
        </div>
      </div>

      <div className="panel">
        <h3>Equipo</h3>
        <div className="tabla-scroll">
          <table>
            <thead>
              <tr>
                <th>Integrante</th>
                <th>No. de cuenta</th>
              </tr>
            </thead>
            <tbody>
              {INTEGRANTES.map((i) => (
                <tr key={i.cuenta}>
                  <td>{i.nombre}</td>
                  <td className="mono">{i.cuenta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
