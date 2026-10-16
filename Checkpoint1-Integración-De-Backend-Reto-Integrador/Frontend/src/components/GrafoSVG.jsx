import { useMemo } from "react";

const ANCHO = 800;
const ALTO = 520;
const MARGEN = 40;
const RADIO = 17;

// Posición de cada nodo: las coordenadas recibidas escaladas al lienzo o, si no
// hay, un acomodo circular.
function posiciones(nodos, coordenadas) {
  const conCoordenadas = coordenadas && nodos.every((n) => coordenadas[n]);
  if (!conCoordenadas) {
    const r = Math.min(ANCHO, ALTO) / 2 - MARGEN;
    return Object.fromEntries(
      nodos.map((n, i) => {
        const angulo = (2 * Math.PI * i) / nodos.length - Math.PI / 2;
        return [n, [ANCHO / 2 + r * Math.cos(angulo), ALTO / 2 + r * Math.sin(angulo)]];
      })
    );
  }
  const xs = nodos.map((n) => coordenadas[n][0]);
  const ys = nodos.map((n) => coordenadas[n][1]);
  const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const escala = Math.min(
    (ANCHO - 2 * MARGEN) / (maxX - minX || 1),
    (ALTO - 2 * MARGEN) / (maxY - minY || 1)
  );
  const dx = (ANCHO - (maxX - minX) * escala) / 2;
  const dy = (ALTO - (maxY - minY) * escala) / 2;
  return Object.fromEntries(
    nodos.map((n) => [
      n,
      [dx + (coordenadas[n][0] - minX) * escala, dy + (coordenadas[n][1] - minY) * escala],
    ])
  );
}

const colorNivel = (nivel, maximo) => `hsl(${250 - (nivel / Math.max(1, maximo)) * 200} 75% 60%)`;

/**
 * lista: {nodo: [[vecino, peso], ...]}
 * ruta: nodos de la ruta a resaltar (para un ciclo, el último es igual al primero)
 * orden: orden de visita, se numera junto a cada nodo
 * niveles: {nodo: nivel} para colorear el alcance máximo
 */
export default function GrafoSVG({ lista, coordenadas, dirigido = true, ruta = [], orden = [], niveles }) {
  const nodos = useMemo(() => {
    const todos = new Set(Object.keys(lista));
    Object.values(lista).forEach((vs) => vs.forEach(([v]) => todos.add(v)));
    return [...todos];
  }, [lista]);

  const pos = useMemo(() => posiciones(nodos, coordenadas), [nodos, coordenadas]);

  const aristas = useMemo(() => {
    const vistas = new Map();
    Object.entries(lista).forEach(([u, vecinos]) =>
      vecinos.forEach(([v, w]) => {
        const clave = dirigido ? `${u}→${v}` : [u, v].sort().join("—");
        if (!vistas.has(clave)) vistas.set(clave, { u, v, w });
      })
    );
    return [...vistas.values()];
  }, [lista, dirigido]);

  const enRuta = useMemo(() => {
    const pares = new Set();
    ruta.slice(1).forEach((v, i) => {
      const u = ruta[i];
      pares.add(`${u}→${v}`);
      if (!dirigido) pares.add(`${v}→${u}`);
    });
    return pares;
  }, [ruta, dirigido]);

  const nodosRuta = new Set(ruta);
  const extremos = new Set(ruta.length ? [ruta[0], ruta[ruta.length - 1]] : []);
  const ordenDe = Object.fromEntries(orden.map((n, i) => [n, i + 1]));
  const maxNivel = niveles ? Math.max(...Object.values(niveles)) : 0;

  return (
    <svg
      className="grafo-svg"
      viewBox={`0 0 ${ANCHO} ${ALTO}`}
      role="img"
      aria-label={`Grafo con ${nodos.length} nodos${ruta.length ? `; ruta ${ruta.join(" → ")}` : ""}`}
    >
      <defs>
        {["normal", "ruta"].map((tipo) => (
          <marker
            key={tipo}
            id={`flecha-${tipo}`}
            viewBox="0 0 10 10"
            refX="10"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M0,0 L10,5 L0,10 z" className={tipo === "ruta" ? "flecha-ruta" : "flecha"} fill={tipo === "ruta" ? "var(--ruta)" : "var(--texto-suave)"} />
          </marker>
        ))}
      </defs>

      {aristas.map(({ u, v, w }) => {
        const [x1, y1] = pos[u];
        const [x2, y2] = pos[v];
        const largo = Math.hypot(x2 - x1, y2 - y1) || 1;
        const [ux, uy] = [(x2 - x1) / largo, (y2 - y1) / largo];
        const resaltada = enRuta.has(`${u}→${v}`) || (!dirigido && enRuta.has(`${v}→${u}`));
        const fin = dirigido ? RADIO + 3 : RADIO;
        return (
          <g key={`${u}-${v}`}>
            <line
              className={`arista ${resaltada ? "ruta" : ""}`}
              x1={x1 + ux * RADIO}
              y1={y1 + uy * RADIO}
              x2={x2 - ux * fin}
              y2={y2 - uy * fin}
              strokeWidth={resaltada ? 4 : 1.5}
              markerEnd={dirigido ? `url(#flecha-${resaltada ? "ruta" : "normal"})` : undefined}
            />
            <text className={`peso ${resaltada ? "ruta" : ""}`} x={(x1 + x2) / 2} y={(y1 + y2) / 2 - 4} textAnchor="middle">
              {w}
            </text>
          </g>
        );
      })}

      {nodos.map((n) => {
        const [x, y] = pos[n];
        const clase = extremos.has(n) ? "extremo" : nodosRuta.has(n) ? "ruta" : "";
        const relleno = niveles && n in niveles && !extremos.has(n) ? colorNivel(niveles[n], maxNivel) : undefined;
        return (
          <g key={n} className={`nodo ${clase}`}>
            <circle cx={x} cy={y} r={RADIO} style={relleno ? { fill: relleno } : undefined} />
            <text x={x} y={y}>
              {n}
            </text>
            {ordenDe[n] && (
              <text className="orden" x={x + RADIO + 2} y={y - RADIO + 2}>
                {ordenDe[n]}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
