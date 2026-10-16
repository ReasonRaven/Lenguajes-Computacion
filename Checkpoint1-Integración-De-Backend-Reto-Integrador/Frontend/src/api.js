// Cliente del backend (Backend-Unificado). En desarrollo Vite reenvía /api al
// backend; con VITE_API_URL se puede apuntar a otro servidor.
const BASE = import.meta.env.VITE_API_URL ?? "/api";

function mensajeDeError(status, cuerpo) {
  const detalle = cuerpo?.detail;
  if (Array.isArray(detalle)) {
    // Errores de validación de FastAPI/Pydantic: [{loc, msg}, ...]
    return detalle
      .map((e) => {
        const msg = String(e.msg ?? "").replace(/^Value error, /, "");
        const campo = (e.loc ?? []).filter((p) => p !== "body").join(".");
        return campo && !msg.includes(campo) ? `${campo}: ${msg}` : msg;
      })
      .join(" · ");
  }
  if (typeof detalle === "string") return detalle;
  return `El servidor respondió ${status}.`;
}

async function procesar(respuesta) {
  const tipo = respuesta.headers.get("content-type") ?? "";
  const cuerpo = tipo.includes("json") ? await respuesta.json() : await respuesta.text();
  if (!respuesta.ok) throw new Error(mensajeDeError(respuesta.status, cuerpo));
  return cuerpo;
}

async function solicitar(ruta, opciones) {
  let respuesta;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, opciones);
  } catch {
    throw new Error(
      "No se pudo conectar con el backend. ¿Está corriendo `uvicorn main:app` en Backend-Unificado?"
    );
  }
  if (respuesta.status >= 502 && respuesta.status <= 504) {
    throw new Error(
      "No se pudo conectar con el backend. ¿Está corriendo `uvicorn main:app` en Backend-Unificado?"
    );
  }
  return procesar(respuesta);
}

export function post(ruta, body) {
  return solicitar(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function postArchivo(ruta, archivo) {
  const datos = new FormData();
  datos.append("archivo", archivo);
  return solicitar(ruta, { method: "POST", body: datos });
}
