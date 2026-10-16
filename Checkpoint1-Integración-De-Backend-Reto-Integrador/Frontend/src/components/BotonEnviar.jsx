export default function BotonEnviar({ cargando, children, ...props }) {
  return (
    <button type="submit" className={`btn primario ${cargando ? "cargando" : ""}`} disabled={cargando} {...props}>
      {cargando ? "Calculando…" : children}
    </button>
  );
}
