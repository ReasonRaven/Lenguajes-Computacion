// Editor de la tabla de transición δ.
// automata = { simbolos: ["a", "b"], filas: [{ nombre, celdas: [...], lambda }], inicial, finales }
// Cada celda es texto: en AFD un estado; en AFND estados separados por comas.

export function automataDesdeEjemplo(ej) {
  return {
    simbolos: [...ej.simbolos],
    filas: ej.estados.map((q) => ({
      nombre: q,
      celdas: ej.simbolos.map((s) => ej.tabla[q]?.[s] ?? ""),
      lambda: ej.tabla[q]?.["λ"] ?? "",
    })),
    inicial: ej.inicial,
    finales: [...ej.finales],
  };
}

const destinos = (texto) =>
  texto
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

// Tabla en el formato del backend: estado -> símbolo -> destino(s).
export function tablaParaApi(automata, { deterministico, conLambda }) {
  return Object.fromEntries(
    automata.filas.map((f) => {
      const fila = Object.fromEntries(
        automata.simbolos.map((s, i) => [
          s,
          deterministico ? destinos(f.celdas[i])[0] ?? null : destinos(f.celdas[i]),
        ])
      );
      if (conLambda) fila["λ"] = destinos(f.lambda);
      return [f.nombre, fila];
    })
  );
}

export default function TablaTransiciones({ automata, onChange, deterministico, conLambda }) {
  const { simbolos, filas, inicial, finales } = automata;
  const cambiar = (parcial) => onChange({ ...automata, ...parcial });

  const setCelda = (i, j, valor) =>
    cambiar({
      filas: filas.map((f, k) =>
        k === i ? { ...f, celdas: f.celdas.map((c, l) => (l === j ? valor : c)) } : f
      ),
    });

  const renombrarEstado = (i, nombre) => {
    const anterior = filas[i].nombre;
    cambiar({
      filas: filas.map((f, k) => (k === i ? { ...f, nombre } : f)),
      inicial: inicial === anterior ? nombre : inicial,
      finales: finales.map((q) => (q === anterior ? nombre : q)),
    });
  };

  const agregarEstado = () => {
    let k = filas.length;
    while (filas.some((f) => f.nombre === `q${k}`)) k++;
    cambiar({ filas: [...filas, { nombre: `q${k}`, celdas: simbolos.map(() => ""), lambda: "" }] });
  };

  const quitarEstado = (i) => {
    const nombre = filas[i].nombre;
    const restantes = filas.filter((_, k) => k !== i);
    cambiar({
      filas: restantes,
      inicial: inicial === nombre ? restantes[0]?.nombre ?? "" : inicial,
      finales: finales.filter((q) => q !== nombre),
    });
  };

  const agregarSimbolo = () => {
    const libre = "abcdefghijklmnopqrstuvwxyz0123456789".split("").find((c) => !simbolos.includes(c)) ?? "?";
    cambiar({ simbolos: [...simbolos, libre], filas: filas.map((f) => ({ ...f, celdas: [...f.celdas, ""] })) });
  };

  const quitarSimbolo = (j) =>
    cambiar({
      simbolos: simbolos.filter((_, l) => l !== j),
      filas: filas.map((f) => ({ ...f, celdas: f.celdas.filter((_, l) => l !== j) })),
    });

  const alternarFinal = (q) =>
    cambiar({ finales: finales.includes(q) ? finales.filter((x) => x !== q) : [...finales, q] });

  return (
    <div>
      <div className="tabla-scroll tabla-transiciones">
        <table>
          <thead>
            <tr>
              <th>δ</th>
              {simbolos.map((s, j) => (
                <th key={j}>
                  <div className="fila" style={{ flexWrap: "nowrap", gap: "0.2rem", alignItems: "center" }}>
                    <input
                      type="text"
                      value={s}
                      maxLength={3}
                      aria-label={`Símbolo ${j + 1}`}
                      onChange={(e) =>
                        cambiar({ simbolos: simbolos.map((x, l) => (l === j ? e.target.value : x)) })
                      }
                    />
                    <button type="button" className="btn-icono" aria-label={`Quitar símbolo ${s}`} onClick={() => quitarSimbolo(j)}>
                      ×
                    </button>
                  </div>
                </th>
              ))}
              {conLambda && <th>λ</th>}
              <th>
                <button type="button" className="btn chico" onClick={agregarSimbolo}>
                  + símbolo
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {filas.map((f, i) => (
              <tr key={i}>
                <td className="estado">
                  <input
                    type="text"
                    value={f.nombre}
                    aria-label={`Nombre del estado ${i + 1}`}
                    onChange={(e) => renombrarEstado(i, e.target.value)}
                  />
                  <div className="marcas">
                    <label>
                      <input type="radio" name="inicial" checked={inicial === f.nombre} onChange={() => cambiar({ inicial: f.nombre })} />
                      inicial
                    </label>
                    <label>
                      <input type="checkbox" checked={finales.includes(f.nombre)} onChange={() => alternarFinal(f.nombre)} />
                      final
                    </label>
                  </div>
                </td>
                {simbolos.map((s, j) => (
                  <td key={j}>
                    <input
                      type="text"
                      value={f.celdas[j]}
                      placeholder={deterministico ? "estado" : "q0, q1"}
                      aria-label={`δ(${f.nombre}, ${s})`}
                      onChange={(e) => setCelda(i, j, e.target.value)}
                    />
                  </td>
                ))}
                {conLambda && (
                  <td>
                    <input
                      type="text"
                      value={f.lambda}
                      placeholder="q0, q1"
                      aria-label={`δ(${f.nombre}, λ)`}
                      onChange={(e) =>
                        cambiar({ filas: filas.map((x, k) => (k === i ? { ...x, lambda: e.target.value } : x)) })
                      }
                    />
                  </td>
                )}
                <td>
                  <button type="button" className="btn-icono" aria-label={`Quitar estado ${f.nombre}`} onClick={() => quitarEstado(i)}>
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="fila" style={{ marginTop: "0.5rem" }}>
        <button type="button" className="btn chico" onClick={agregarEstado}>
          + estado
        </button>
        <span className="suave">
          {deterministico
            ? "Cada celda: un solo estado destino (vacía = sin transición)."
            : "Cada celda: estados destino separados por comas (vacía = ∅)."}
        </span>
      </div>
    </div>
  );
}
