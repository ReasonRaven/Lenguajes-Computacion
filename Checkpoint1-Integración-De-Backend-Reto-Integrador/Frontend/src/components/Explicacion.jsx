// Capa de interpretación: muestra el campo `explicacion` que manda el backend.
export default function Explicacion({ texto, titulo = "¿Qué pasó y por qué?" }) {
  if (!texto) return null;
  return (
    <div className="explicacion" role="note">
      <span className="icono" aria-hidden="true">💡</span>
      <div>
        <h4>{titulo}</h4>
        <p>{texto}</p>
      </div>
    </div>
  );
}
