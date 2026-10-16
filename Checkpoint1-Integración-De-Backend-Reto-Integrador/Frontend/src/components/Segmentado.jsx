// Grupo de botones donde solo uno está activo (pestañas internas y selectores cortos).
export default function Segmentado({ opciones, valor, onChange, etiqueta }) {
  return (
    <div className="segmentado" role="tablist" aria-label={etiqueta}>
      {opciones.map((o) => {
        const id = typeof o === "string" ? o : o.valor;
        const texto = typeof o === "string" ? o : o.texto;
        return (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={valor === id}
            className={valor === id ? "activo" : ""}
            onClick={() => onChange(id)}
          >
            {texto}
          </button>
        );
      })}
    </div>
  );
}
