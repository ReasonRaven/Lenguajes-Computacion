import { useEffect, useState } from "react";
import Inicio from "./modulos/Inicio.jsx";
import Modulo1 from "./modulos/Modulo1.jsx";
import Modulo2 from "./modulos/Modulo2.jsx";
import Modulo3 from "./modulos/Modulo3.jsx";
import { INTEGRANTES } from "./datos.js";

const SECCIONES = [
  { id: "inicio", titulo: "Inicio", componente: Inicio },
  { id: "modulo1", titulo: "1 · Lenguajes y autómatas", componente: Modulo1 },
  { id: "modulo2", titulo: "2 · Logística y rutas", componente: Modulo2 },
  { id: "modulo3", titulo: "3 · Escalabilidad", componente: Modulo3 },
];

function seccionDelHash() {
  const id = window.location.hash.replace("#", "");
  return SECCIONES.some((s) => s.id === id) ? id : "inicio";
}

export default function App() {
  const [actual, setActual] = useState(seccionDelHash);

  useEffect(() => {
    const alCambiar = () => setActual(seccionDelHash());
    window.addEventListener("hashchange", alCambiar);
    return () => window.removeEventListener("hashchange", alCambiar);
  }, []);

  const ir = (id) => {
    window.location.hash = id;
    window.scrollTo({ top: 0 });
  };

  return (
    <div className="app">
      <header className="encabezado">
        <div className="marca">
          <span className="logo" aria-hidden="true">λ</span>
          <div>
            <h1>Laboratorio de Computación</h1>
            <p>Autómatas, rutas y complejidad algorítmica</p>
          </div>
        </div>
        <nav className="nav" aria-label="Módulos">
          {SECCIONES.map((s) => (
            <button
              key={s.id}
              className={`nav-btn ${actual === s.id ? "activo" : ""} ${s.id}`}
              aria-current={actual === s.id ? "page" : undefined}
              onClick={() => ir(s.id)}
            >
              {s.titulo}
            </button>
          ))}
        </nav>
      </header>

      <main className="contenido">
        {/* Los módulos se montan una vez y se ocultan, para conservar lo capturado al cambiar de pestaña. */}
        {SECCIONES.map(({ id, componente: Componente }) => (
          <section key={id} hidden={actual !== id}>
            <Componente ir={ir} />
          </section>
        ))}
      </main>

      <footer className="pie">
        Reto Integrador (Examen parcial #2) · Lenguajes de la Computación ·{" "}
        {INTEGRANTES.map((i) => i.nombre).join(" · ")}
      </footer>
    </div>
  );
}
