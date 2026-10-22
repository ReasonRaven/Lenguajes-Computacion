// Capa de interpretación: muestra el campo `explicacion` que manda el backend.
// `ia` (campo `explicacion_ia`) indica si el texto lo generó Gemini o es la
// plantilla de respaldo.
export default function Explicacion({ texto, ia, titulo = "¿Qué pasó y por qué?" }) {
  if (!texto) return null;
  return (
    <div className="explicacion" role="note">
      <span className="icono" aria-hidden="true">💡</span>
      <div>
        <h4>{titulo}</h4>
        <p>{texto}</p>
        {ia !== undefined && (
          <span className="origen">
            {ia ? "✨ Generada con IA" : "Explicación predefinida (IA no disponible)"}
          </span>
        )}
      </div>
    </div>
  );
}
