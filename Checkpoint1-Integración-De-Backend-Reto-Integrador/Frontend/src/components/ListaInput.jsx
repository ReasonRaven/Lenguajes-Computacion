import { useState } from "react";

export const mostrar = (cadena) => (cadena === "" ? "λ" : cadena);

// Lista editable como chips. Enter o coma agregan; "λ" (o dejarlo vacío con Enter
// si `permitirVacia`) agrega la cadena vacía.
export default function ListaInput({
  valores,
  onChange,
  placeholder = "Escribe y presiona Enter",
  permitirVacia = true,
  numerica = false,
  etiqueta,
}) {
  const [texto, setTexto] = useState("");

  const agregar = (crudo) => {
    let partes = crudo.split(",").map((p) => p.trim());
    if (crudo.trim() === "" || crudo.trim() === "λ") partes = permitirVacia ? [""] : [];
    partes = partes.map((p) => (p === "λ" ? "" : p));
    if (numerica) {
      partes = partes.filter((p) => p !== "" && !Number.isNaN(Number(p))).map(Number);
    }
    const nuevos = partes.filter((p) => !valores.includes(p) || numerica);
    if (nuevos.length) onChange([...valores, ...nuevos]);
    setTexto("");
  };

  const alTeclear = (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      agregar(texto);
    } else if (e.key === "Backspace" && texto === "" && valores.length) {
      onChange(valores.slice(0, -1));
    }
  };

  return (
    <div className="chips">
      {valores.map((v, i) => (
        <span className="chip" key={`${v}-${i}`}>
          {numerica ? v : mostrar(v)}
          <button
            type="button"
            className="btn-icono"
            aria-label={`Quitar ${numerica ? v : mostrar(v)}`}
            onClick={() => onChange(valores.filter((_, j) => j !== i))}
          >
            ×
          </button>
        </span>
      ))}
      <input
        type="text"
        value={texto}
        aria-label={etiqueta}
        placeholder={valores.length ? "" : placeholder}
        onChange={(e) => setTexto(e.target.value)}
        onKeyDown={alTeclear}
        onBlur={() => texto.trim() && agregar(texto)}
      />
    </div>
  );
}

export function Conjunto({ elementos, max = 200 }) {
  if (!elementos.length) return <span className="suave">∅ (conjunto vacío)</span>;
  return (
    <div className="conjunto">
      {elementos.slice(0, max).map((e, i) => (
        <span className="chip solo" key={i}>
          {mostrar(e)}
        </span>
      ))}
      {elementos.length > max && <span className="suave">… y {elementos.length - max} más</span>}
    </div>
  );
}
