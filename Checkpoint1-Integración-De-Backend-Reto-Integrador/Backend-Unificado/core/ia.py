"""Cliente de Google Gemini para la capa de interpretación.

Genera en el momento el texto de `explicacion` a partir de los datos concretos de
cada resultado y de la base teórica de `explicaciones.TEORIA`. Usa el SDK `openai`
contra el endpoint de Gemini compatible con OpenAI. Se configura con variables de
entorno (ver `.env.example`):

- `GEMINI_API_KEY`: sin ella no se llama a la API (se obtiene en Google AI Studio).
- `GEMINI_MODEL`: modelo a usar (por defecto `gemini-3.5-flash-lite`).
- `GEMINI_TIMEOUT`: segundos máximos por llamada (por defecto 20).

Si falta la key o la llamada falla, las funciones devuelven `None` y quien las
llama usa la plantilla de respaldo.
"""

import json
import logging
import os

log = logging.getLogger(__name__)

URL_GEMINI = "https://generativelanguage.googleapis.com/v1beta/openai/"
MAXIMO_LISTA = 30

SISTEMA = (
    "Eres el asistente de una aplicación educativa de Lenguajes Computacionales (autómatas, "
    "lenguajes formales, grafos, búsqueda y complejidad algorítmica). Tu público son "
    "estudiantes de nuevo ingreso sin conocimientos especializados. Recibirás una tarea, los "
    "datos concretos de una operación que el sistema ya calculó y una base teórica de "
    "referencia. Explica en español qué pasó con ESOS datos y por qué, apoyándote en la "
    "teoría. Reglas: usa solo los datos recibidos y no inventes cifras ni resultados; no "
    "vuelvas a calcular nada, el resultado ya es correcto; escribe texto plano sin Markdown, "
    "listas ni encabezados; puedes usar notación como λ, δ*, ∈, O(n log n); sé claro y breve."
)

_cliente = None


def _obtener_cliente():
    global _cliente
    if _cliente is None:
        clave = os.getenv("GEMINI_API_KEY", "").strip()
        if not clave:
            return None
        from openai import OpenAI

        _cliente = OpenAI(
            api_key=clave,
            base_url=URL_GEMINI,
            timeout=float(os.getenv("GEMINI_TIMEOUT", "20")),
            max_retries=1,
        )
    return _cliente


def _recortar(valor):
    """Acorta listas y diccionarios largos para no mandar entradas enormes."""
    if isinstance(valor, list):
        recortada = [_recortar(v) for v in valor[:MAXIMO_LISTA]]
        if len(valor) > MAXIMO_LISTA:
            recortada.append(f"... ({len(valor) - MAXIMO_LISTA} elementos más)")
        return recortada
    if isinstance(valor, dict):
        claves = list(valor)[:MAXIMO_LISTA]
        recortado = {str(k): _recortar(valor[k]) for k in claves}
        if len(valor) > MAXIMO_LISTA:
            recortado["..."] = f"{len(valor) - MAXIMO_LISTA} entradas más"
        return recortado
    if isinstance(valor, tuple):
        return _recortar(list(valor))
    return valor


def _mensaje(tarea: str, datos: dict, teoria: str) -> str:
    return (
        f"Tarea: {tarea}\n\n"
        f"Datos (JSON):\n{json.dumps(_recortar(datos), ensure_ascii=False, default=str)}\n\n"
        f"Base teórica de referencia:\n{teoria}"
    )


def _completar(contenido: str, **opciones) -> str | None:
    try:
        cliente = _obtener_cliente()
        if cliente is None:
            return None
        respuesta = cliente.chat.completions.create(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            messages=[
                {"role": "system", "content": SISTEMA},
                {"role": "user", "content": contenido},
            ],
            temperature=0.4,
            **opciones,
        )
        texto = (respuesta.choices[0].message.content or "").strip()
        return texto or None
    except Exception as error:  # sin `openai` instalado, red, cuota, key inválida, timeout...
        log.warning("No se pudo generar la explicación con Gemini: %s", error)
        return None


def generar(tarea: str, datos: dict, teoria: str) -> str | None:
    """Un solo párrafo de 3 a 5 oraciones."""
    return _completar(
        _mensaje(tarea, datos, teoria)
        + "\n\nResponde con un solo párrafo de 3 a 5 oraciones."
    )


def generar_json(
    tarea: str, datos: dict, teoria: str, lista: str, cantidad: int
) -> dict | None:
    """Varios textos en una sola llamada: `{"general": str, lista: [str] * cantidad}`.

    Devuelve `None` si la respuesta no tiene esa forma."""
    forma = (
        f'\n\nResponde SOLO con un objeto JSON de la forma {{"general": "...", '
        f'"{lista}": ["...", ...]}}. "general" es un párrafo de 3 a 5 oraciones sobre todo '
        f'el resultado; "{lista}" tiene exactamente {cantidad} textos de 1 o 2 oraciones, '
        f"uno por elemento y en el mismo orden en que aparecen en los datos."
    )
    texto = _completar(
        _mensaje(tarea, datos, teoria) + forma, response_format={"type": "json_object"}
    )
    if texto is None:
        return None
    try:
        objeto = json.loads(texto)
    except json.JSONDecodeError:
        log.warning("Gemini devolvió un JSON inválido: %s", texto[:200])
        return None
    general, elementos = objeto.get("general"), objeto.get(lista)
    if (
        not isinstance(general, str)
        or not isinstance(elementos, list)
        or len(elementos) != cantidad
        or not all(isinstance(e, str) for e in elementos)
    ):
        log.warning("La respuesta de Gemini no tiene la forma esperada.")
        return None
    return {"general": general.strip(), lista: [e.strip() for e in elementos]}
