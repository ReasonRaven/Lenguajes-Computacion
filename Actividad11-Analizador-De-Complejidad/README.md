# Actividad 11. Analizador de complejidad

**Nombre de la actividad:** Actividad 11. Analizador de complejidad (Big-O y Big-Ω)

## Equipo

| Nombre completo | No. de cuenta |
|---|---|
| Jonathan Hernández Lazcano | 200417 |
| Camila Rodriguez Rosas | 194100 |

## Instrucciones

> Implementa una API que analice el contenido de un archivo que contenga algún programa y devuelva
> un archivo que añada en forma de comentarios la complejidad (notación Big-O) línea por línea y un
> bloque final dentro del archivo con el resumen de la complejidad identificada, donde se indique la
> suma de las complejidades individuales y aquella que se identificó como la complejidad de mayor
> grado.
>
> Escalando el backend previamente desarrollado (analizador de autómatas), agrega 2 endpoints
> adicionales, uno que devuelva la complejidad del programa en el peor de los casos (Big-O) y otro
> que devuelva la complejidad en el mejor de los casos (Big-Omega).
>
> **Entregable:** un archivo .md que documente detalladamente la operación de los nuevos endpoints
> agregados.

Este documento es ese entregable. Los algoritmos con los que se probó la API son los de
[`img/Algoritmos.png`](img/Algoritmos.png): `raizCuadrada`, `factorial`, `burbuja` y
`ordenacionBinaria`.

## Descripción

El proyecto parte del backend de la
[Actividad 6](../Actividad6-Implementación-Cadenas-AFD-AFND-FastAPI/README.md) (evaluadores de
AFD y AFND en FastAPI). Se copió tal cual a esta carpeta y se le agregó un módulo nuevo,
**Complejidad**, con dos endpoints:

| Endpoint | Caso | Notación |
|---|---|---|
| `POST /complejidad/peor-caso` | Peor caso: siempre el camino más costoso | **Big-O** `O(·)` |
| `POST /complejidad/mejor-caso` | Mejor caso: el camino más barato | **Big-Omega** `Ω(·)` |

Los dos reciben un archivo `.py` y devuelven **el mismo programa** con:

1. Un comentario al final de cada línea de código con su complejidad.
2. Un comentario en cada `def` con la complejidad total de la función.
3. Un **bloque final de resumen** que indica, por función y para el programa completo, la **suma de
   las complejidades individuales** y la **complejidad de mayor grado**.

El programa recibido **no se ejecuta**: se analiza de forma estática con el módulo `ast` de Python.

## Cómo ejecutar

```bash
cd Actividad-11-Analizador-De-Complejidad

python3 -m venv .venv
source .venv/bin/activate                     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Levantar la API (documentación interactiva en http://127.0.0.1:8000/docs)
uvicorn main:app --reload
```

`python-multipart` es una dependencia nueva respecto a la Actividad 6: FastAPI la necesita para
recibir archivos (`UploadFile`).

## Estructura

```
Actividad-11-Analizador-De-Complejidad/
├── main.py                    # App de FastAPI: monta los routers de AFD, AFND y Complejidad
├── core/
│   ├── automatas.py, afd.py, afnd.py   # Lógica de la Actividad 6 (sin cambios)
│   └── complejidad.py         # NUEVO: analizador de complejidad (sin dependencias de FastAPI)
├── routers/
│   ├── afd.py, afnd.py        # Endpoints de la Actividad 6 (sin cambios)
│   └── complejidad.py         # NUEVO: /complejidad/peor-caso y /complejidad/mejor-caso
├── ejemplos/
│   ├── algoritmos.py          # Los 4 algoritmos de img/Algoritmos.png
│   └── salida/                # Archivos devueltos por la API para algoritmos.py
├── img/Algoritmos.png
└── requirements.txt
```

## Endpoints

Todos los endpoints de la API:

| Endpoint | Descripción | Origen |
|---|---|---|
| `GET /` | Verificación de estado (`{"status": "ok"}`) | Actividad 6 |
| `POST /afd/evaluar` | Evalúa cadenas sobre un AFD | Actividad 6 |
| `POST /afnd/evaluar` | Evalúa cadenas sobre un AFND | Actividad 6 |
| `POST /complejidad/peor-caso` | Complejidad en el peor caso (Big-O) | **Nuevo** |
| `POST /complejidad/mejor-caso` | Complejidad en el mejor caso (Big-Ω) | **Nuevo** |

Los dos endpoints nuevos tienen exactamente la misma interfaz; solo cambia el caso que analizan.

### Petición

La petición es `multipart/form-data` (subida de archivo), no JSON.

| Parámetro | Dónde | Tipo | Obligatorio | Descripción |
|---|---|---|---|---|
| `archivo` | cuerpo (form-data) | archivo | Sí | Programa en Python, codificado en UTF-8 |
| `formato` | query string | `archivo` \| `json` | No (por defecto `archivo`) | Qué devuelve el endpoint |

### Respuesta

| `formato` | Código | `Content-Type` | Contenido |
|---|---|---|---|
| `archivo` | `200` | `text/x-python; charset=utf-8` | El programa anotado, como descarga (`Content-Disposition: attachment`) con nombre `<archivo>_peor_caso.py` o `<archivo>_mejor_caso.py` |
| `json` | `200` | `application/json` | El análisis estructurado (ver abajo), que incluye también el archivo anotado |
| — | `422` | `application/json` | El archivo no es UTF-8, no es Python válido, o falta el campo `archivo` |

Ejemplo de error:

```json
{ "detail": "El archivo no es un programa de Python válido: invalid syntax (línea 1)." }
```

#### Estructura de la respuesta JSON

| Campo | Tipo | Descripción |
|---|---|---|
| `archivo` | texto | Nombre del archivo recibido |
| `caso` | `"peor"` \| `"mejor"` | Caso analizado |
| `notacion` | `"Big-O"` \| `"Big-Omega"` | Notación usada |
| `funciones` | lista | Un elemento por función (y uno `<módulo>` para el código fuera de funciones) |
| `funciones[].nombre` | texto | Nombre de la función (`Clase.metodo` en los métodos) |
| `funciones[].linea` | entero | Línea del `def` |
| `funciones[].lineas` | lista | Por cada línea: `linea`, `codigo`, `complejidad`, `cuenta` (si entra en la suma) y `nota` |
| `funciones[].suma` | texto | Suma de las complejidades individuales, en el orden del código |
| `funciones[].suma_agrupada` | texto | La misma suma con los términos iguales agrupados |
| `funciones[].recurrencia` | texto \| `null` | Recurrencia resuelta, si la función es recursiva |
| `funciones[].complejidad` | texto | Complejidad de mayor grado de la función |
| `programa.suma` | texto | Suma de las complejidades de todas las funciones |
| `programa.suma_agrupada` | texto | Todas las líneas del programa, agrupadas |
| `programa.complejidad` | texto | Complejidad de mayor grado del programa |
| `programa.funciones_mayor_grado` | lista | Funciones que alcanzan esa complejidad |
| `archivo_anotado` | texto | El mismo contenido que devuelve `formato=archivo` |

### Cómo llamarlos

**Con `curl`** (desde la carpeta de la actividad, con la API levantada):

```bash
# Peor caso: descarga ejemplos/salida/algoritmos_peor_caso.py
curl -X POST "http://127.0.0.1:8000/complejidad/peor-caso" \
     -F "archivo=@ejemplos/algoritmos.py" -OJ

# Mejor caso, como JSON
curl -X POST "http://127.0.0.1:8000/complejidad/mejor-caso?formato=json" \
     -F "archivo=@ejemplos/algoritmos.py"
```

(`-OJ` guarda la respuesta con el nombre que indica el encabezado `Content-Disposition`.)

**Desde Swagger** (`http://127.0.0.1:8000/docs`): abrir el grupo **Complejidad**, elegir el
endpoint, *Try it out*, seleccionar el archivo en `archivo`, elegir el `formato` y pulsar
*Execute*. Con `formato=archivo` aparece el enlace *Download file*.

**Desde Python:**

```python
import httpx

with open("ejemplos/algoritmos.py", "rb") as f:
    r = httpx.post(
        "http://127.0.0.1:8000/complejidad/peor-caso",
        files={"archivo": ("algoritmos.py", f)},
        params={"formato": "json"},
    )
print(r.json()["programa"]["complejidad"])   # O(n²)
```

## Cómo funciona el análisis

Al procesar un archivo, el endpoint:

1. Decodifica el archivo como UTF-8 y lo convierte en un árbol sintáctico con `ast.parse`. Si
   falla, responde `422`.
2. Registra todas las funciones del archivo, incluidos los métodos de las clases.
3. Recorre cada función sentencia por sentencia y lleva un **multiplicador**: cuántas veces se
   ejecuta el bloque actual (el producto de las iteraciones de los ciclos que lo contienen).
4. A cada línea le asigna `costo = multiplicador × costo propio de la sentencia`.
5. La complejidad de la función es el término de **mayor grado** entre sus líneas (las demás son
   términos de la suma que se desprecian asintóticamente).
6. Escribe los comentarios y el bloque de resumen.

Las complejidades se representan como términos `2ⁿ · nᵃ · logᵇ n`. Multiplicarlas suma los
exponentes, y se ordenan por crecimiento: `1 < log n < n < n log n < n² < … < 2ⁿ`.

### Reglas del peor caso (Big-O)

| Construcción | Iteraciones / costo | Ejemplo |
|---|---|---|
| Asignación, comparación, aritmética, `return`, indexación | `O(1)` | `x = n`, `lista[j] > lista[j+1]` |
| `for` sobre `range(...)` que depende de una variable | `O(n)` iteraciones | `for i in range(2, n + 1)` |
| `for` sobre una colección | `O(n)` iteraciones | `for x in lista` |
| `for` sobre un rango o literal **constante** | `O(1)` iteraciones | `for k in range(10)` |
| `while` donde una variable de la condición se divide o multiplica por una constante en cada vuelta (directa o indirectamente) | `O(log n)` iteraciones | `y = (x + n // x) // 2`; `medio = (izq + der) // 2` → `izq = medio + 1` |
| Cualquier otro `while` | `O(n)` iteraciones | `while i < n: i += 1` |
| Ciclos anidados | se multiplican | `for` dentro de `for` → `O(n²)` |
| `if / elif / else` | la condición más la rama **más costosa** | — |
| Comprensiones de lista/conjunto/diccionario | `O(n)` por cada `for` interno | `[y for y in xs if y == x]` |
| `sorted(xs)`, `xs.sort()` | `O(n log n)` | — |
| `sum`, `min`, `max`, `list`, `set`, `any`, `all` sobre una colección; `x in lista`; `.index`, `.count`, `.remove`, `.insert`, `.join`… | `O(n)` | — |
| Llamada a otra función del mismo archivo | la complejidad de esa función | `self.buscar(xs, x)` |
| Recursión con una llamada a `f(n-1)` | `T(n) = T(n-1) + f ⇒ f·n` | factorial recursivo → `O(n)` |
| Recursión con dos o más llamadas a `f(n-1)` | `O(2ⁿ)` | Fibonacci recursivo |
| Recursión que divide la entrada (`n // 2`) | teorema maestro con `b = 2` | `T(n) = 2T(n/2) + O(n) ⇒ O(n log n)` |

Las líneas de un ciclo tienen el costo de **todas** sus ejecuciones: en `burbuja`, el intercambio
está dentro de dos `for`, así que su línea vale `O(n²)`. El encabezado del ciclo se anota con el
número de veces que se evalúa su condición.

### Reglas del mejor caso (Big-Ω)

Son las mismas, con tres diferencias:

| Situación | Peor caso | Mejor caso |
|---|---|---|
| Ciclo con un `return` o `break` en su cuerpo | iteraciones completas | **1 iteración**: puede salir en la primera vuelta |
| `if / else` con ramas de distinto costo | rama más costosa | **rama más barata**; la otra se marca *no cuenta* |
| `if ...: return` / `raise` al inicio de la función (validación de entrada o caso base) | cuenta como `O(1)` | **se ignora**: se analiza el comportamiento para entradas válidas y de tamaño `n` arbitrario |
| `x in lista`, `.index`, `.remove`, `any`, `all` | `O(n)` | `Ω(1)`: el elemento puede estar al principio |

La tercera regla evita que cualquier función con `if n < 0: return None` salga como `Ω(1)`: con una
entrada inválida la función no hace nada, pero eso no describe su comportamiento cuando `n` crece.
Las líneas ignoradas se siguen anotando, con la nota *«no cuenta en el mejor caso»*, y quedan fuera
de la suma.

## Resultados con los algoritmos de la imagen

Archivo de entrada: [`ejemplos/algoritmos.py`](ejemplos/algoritmos.py). Salidas completas:
[`algoritmos_peor_caso.py`](ejemplos/salida/algoritmos_peor_caso.py) y
[`algoritmos_mejor_caso.py`](ejemplos/salida/algoritmos_mejor_caso.py).

| Algoritmo | Peor caso | Mejor caso | Justificación |
|---|---|---|---|
| `raizCuadrada` | `O(log n)` | `Ω(log n)` | Método de Newton: `y = (x + n // x) // 2` reduce `x` al menos a la mitad en cada vuelta hasta acercarse a √n. El ciclo no tiene salida temprana, así que ambos casos coinciden. |
| `factorial` | `O(n)` | `Ω(n)` | Un `for` de `2` a `n` con cuerpo `O(1)`. La validación `n < 0` se ignora en el mejor caso. |
| `burbuja` | `O(n²)` | `Ω(n²)` | Dos `for` anidados de hasta `n` iteraciones. Esta versión no tiene la bandera `intercambio`, así que recorre la lista completa aunque ya esté ordenada. |
| `ordenacionBinaria` | `O(log n)` | `Ω(1)` | Cada vuelta descarta la mitad del rango (`medio = (izquierda + derecha) // 2`). En el mejor caso el objetivo está justo en `medio` y el `return medio` termina en la primera iteración. |
| **Programa** | **`O(n²)`** | **`Ω(n²)`** | Mayor grado: `burbuja` en ambos casos. |

### Archivo devuelto por `/complejidad/peor-caso`

```python
def raizCuadrada(n):                                             # Complejidad de raizCuadrada: O(log n)
    if n < 0:                                                    # O(1)
        return None                                              # O(1)
    x = n                                                        # O(1)
    y = (x + 1) // 2                                             # O(1)
    while y < x:                                                 # O(log n)
        x = y                                                    # O(log n)
        y = (x + n // x) // 2                                    # O(log n)
    return x                                                     # O(1)


def factorial(n):                                                # Complejidad de factorial: O(n)
    if n < 0:                                                    # O(1)
        return None                                              # O(1)
    resultado = 1                                                # O(1)
    for i in range(2, n + 1):                                    # O(n)
        resultado *= i                                           # O(n)
    return resultado                                             # O(1)


def burbuja(lista):                                              # Complejidad de burbuja: O(n²)
    n = len(lista)                                               # O(1)
    for i in range(n):                                           # O(n)
        for j in range(0, n - i - 1):                            # O(n²)
            if lista[j] > lista[j + 1]:                          # O(n²)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # O(n²)
    return lista                                                 # O(1)


def ordenacionBinaria(lista, objetivo):                          # Complejidad de ordenacionBinaria: O(log n)
    izquierda, derecha = 0, len(lista) - 1                       # O(1)
    while izquierda <= derecha:                                  # O(log n)
        medio = (izquierda + derecha) // 2                       # O(log n)
        if lista[medio] == objetivo:                             # O(log n)
            return medio                                         # O(log n)
        elif lista[medio] < objetivo:                            # O(log n)
            izquierda = medio + 1                                # O(log n)
        else:
            derecha = medio - 1                                  # O(log n)
    return -1                                                    # O(1)


# ==============================================================================
# RESUMEN DE COMPLEJIDAD — PEOR CASO (notación Big-O)
# Archivo analizado: algoritmos.py
# ==============================================================================
#
# raizCuadrada (línea 1)
#   Suma de complejidades : O(1) + O(1) + O(1) + O(1) + O(log n) + O(log n) + O(log n)
#                           + O(1)
#   Términos agrupados    : 5·O(1) + 3·O(log n)
#   Mayor grado           : O(log n)
#
# factorial (línea 12)
#   Suma de complejidades : O(1) + O(1) + O(1) + O(n) + O(n) + O(1)
#   Términos agrupados    : 4·O(1) + 2·O(n)
#   Mayor grado           : O(n)
#
# burbuja (línea 21)
#   Suma de complejidades : O(1) + O(n) + O(n²) + O(n²) + O(n²) + O(1)
#   Términos agrupados    : 2·O(1) + 1·O(n) + 3·O(n²)
#   Mayor grado           : O(n²)
#
# ordenacionBinaria (línea 30)
#   Suma de complejidades : O(1) + O(log n) + O(log n) + O(log n) + O(log n) + O(log n)
#                           + O(log n) + O(log n) + O(1)
#   Términos agrupados    : 2·O(1) + 7·O(log n)
#   Mayor grado           : O(log n)
#
# ------------------------------------------------------------------------------
# PROGRAMA COMPLETO
#   Suma de complejidades : O(log n) + O(n) + O(n²) + O(log n)
#   Términos agrupados    : 13·O(1) + 10·O(log n) + 3·O(n) + 3·O(n²)
#   Mayor grado           : O(n²)  →  burbuja
# ==============================================================================
```

Cómo leer el resumen de `burbuja`: la suma de sus líneas es
`O(1) + O(n) + O(n²) + O(n²) + O(n²) + O(1) = 2·O(1) + O(n) + 3·O(n²)`, y el término de mayor grado,
`O(n²)`, es la complejidad de la función.

### Archivo devuelto por `/complejidad/mejor-caso` (fragmento)

Solo cambian las funciones con validación de entrada y la búsqueda binaria; `burbuja` queda igual
que en el peor caso, pero con `Ω`.

```python
def raizCuadrada(n):                                             # Complejidad de raizCuadrada: Ω(log n)
    if n < 0:                                                    # Ω(1)  ← validación / caso base: no cuenta en el mejor caso
        return None                                              # Ω(1)  ← validación / caso base: no cuenta en el mejor caso
    x = n                                                        # Ω(1)
    y = (x + 1) // 2                                             # Ω(1)
    while y < x:                                                 # Ω(log n)
        x = y                                                    # Ω(log n)
        y = (x + n // x) // 2                                    # Ω(log n)
    return x                                                     # Ω(1)

...

def ordenacionBinaria(lista, objetivo):                          # Complejidad de ordenacionBinaria: Ω(1)
    izquierda, derecha = 0, len(lista) - 1                       # Ω(1)
    while izquierda <= derecha:                                  # Ω(1)  ← puede terminar en la primera iteración (return/break)
        medio = (izquierda + derecha) // 2                       # Ω(1)
        if lista[medio] == objetivo:                             # Ω(1)
            return medio                                         # Ω(1)
        elif lista[medio] < objetivo:                            # Ω(1)
            izquierda = medio + 1                                # Ω(1)
        else:
            derecha = medio - 1                                  # Ω(1)
    return -1                                                    # Ω(1)


# ==============================================================================
# RESUMEN DE COMPLEJIDAD — MEJOR CASO (notación Big-Omega, Ω)
# Archivo analizado: algoritmos.py
# ==============================================================================
#
# raizCuadrada (línea 1)
#   Suma de complejidades : Ω(1) + Ω(1) + Ω(log n) + Ω(log n) + Ω(log n) + Ω(1)
#   Términos agrupados    : 3·Ω(1) + 3·Ω(log n)
#   Mayor grado           : Ω(log n)
#
# ...
#
# ordenacionBinaria (línea 30)
#   Suma de complejidades : Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1)
#   Términos agrupados    : 9·Ω(1)
#   Mayor grado           : Ω(1)
#
# ------------------------------------------------------------------------------
# PROGRAMA COMPLETO
#   Suma de complejidades : Ω(log n) + Ω(n) + Ω(n²) + Ω(1)
#   Términos agrupados    : 16·Ω(1) + 3·Ω(log n) + 3·Ω(n) + 3·Ω(n²)
#   Mayor grado           : Ω(n²)  →  burbuja
#
# Las líneas marcadas como «no cuenta en el mejor caso» quedan fuera de la suma.
# ==============================================================================
```

### Respuesta con `formato=json` (fragmento)

`POST /complejidad/mejor-caso?formato=json`, mostrando solo `ordenacionBinaria`:

```json
{
  "archivo": "algoritmos.py",
  "caso": "mejor",
  "notacion": "Big-Omega",
  "funciones": [
    {
      "nombre": "ordenacionBinaria",
      "linea": 30,
      "lineas": [
        { "linea": 31, "codigo": "izquierda, derecha = 0, len(lista) - 1", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 32, "codigo": "while izquierda <= derecha:", "complejidad": "Ω(1)", "cuenta": true,
          "nota": "puede terminar en la primera iteración (return/break)" },
        { "linea": 33, "codigo": "medio = (izquierda + derecha) // 2", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 34, "codigo": "if lista[medio] == objetivo:", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 35, "codigo": "return medio", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 36, "codigo": "elif lista[medio] < objetivo:", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 37, "codigo": "izquierda = medio + 1", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 39, "codigo": "derecha = medio - 1", "complejidad": "Ω(1)", "cuenta": true, "nota": null },
        { "linea": 40, "codigo": "return -1", "complejidad": "Ω(1)", "cuenta": true, "nota": null }
      ],
      "suma": "Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1)",
      "suma_agrupada": "9·Ω(1)",
      "recurrencia": null,
      "complejidad": "Ω(1)"
    }
  ],
  "programa": {
    "suma": "Ω(log n) + Ω(n) + Ω(n²) + Ω(1)",
    "suma_agrupada": "16·Ω(1) + 3·Ω(log n) + 3·Ω(n) + 3·Ω(n²)",
    "complejidad": "Ω(n²)",
    "funciones_mayor_grado": ["burbuja"]
  },
  "archivo_anotado": "def raizCuadrada(n):   # Complejidad de raizCuadrada: Ω(log n)\n..."
}
```

## Otros casos que reconoce

El analizador no está limitado a los cuatro algoritmos de la imagen. Resultados reales del
endpoint de peor caso con otros programas:

| Código | Resultado |
|---|---|
| `def fact(n): if n <= 1: return 1; return n * fact(n - 1)` | `O(n)`, recurrencia `T(n) = T(n-1) + O(1)` |
| `def fib(n): if n < 2: return n; return fib(n - 1) + fib(n - 2)` | `O(2ⁿ)`, recurrencia `T(n) = 2T(n-1) + O(1)` |
| Método que recorre `xs` y en cada vuelta llama a `self.buscar(xs, x)`, una comprensión `O(n)` | `O(n²)` |
| `for k in range(10): print(k)` a nivel de módulo | `O(1)` (rango constante), reportado como `<módulo>` |

## Limitaciones

El análisis es **estático y heurístico**; calcular la complejidad exacta de cualquier programa es
un problema indecidible. En concreto:

- Solo se analizan programas en **Python**.
- `n` representa el **tamaño de la entrada** (el valor de un número o la longitud de una
  colección); no se distingue entre varias entradas de distinto tamaño (`O(n·m)` se reporta como
  `O(n²)`).
- Un `while` que no divide su variable de control se supone `O(n)`, aunque en realidad pueda dar
  más o menos vueltas.
- No se conocen los tipos: `x in coleccion` se trata como búsqueda en una lista (`O(n)`), aunque
  `coleccion` sea un `set` o un `dict` (`O(1)`).
- Las funciones de bibliotecas externas cuentan como `O(1)`, salvo las integradas listadas en las
  reglas.
- En las funciones recursivas, la línea con la llamada recursiva lleva la complejidad total
  (resultado de la recurrencia); las demás líneas muestran su costo por llamada.
