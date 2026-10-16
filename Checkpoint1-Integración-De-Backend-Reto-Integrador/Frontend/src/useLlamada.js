import { useCallback, useState } from "react";

// Estado de una llamada al backend: cargando, error y datos de la última respuesta.
export function useLlamada() {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [datos, setDatos] = useState(null);

  const ejecutar = useCallback(async (promesa) => {
    setCargando(true);
    setError(null);
    try {
      const resultado = await promesa();
      setDatos(resultado);
      return resultado;
    } catch (e) {
      setError(e.message);
      setDatos(null);
      return null;
    } finally {
      setCargando(false);
    }
  }, []);

  return { cargando, error, datos, ejecutar, setDatos };
}
