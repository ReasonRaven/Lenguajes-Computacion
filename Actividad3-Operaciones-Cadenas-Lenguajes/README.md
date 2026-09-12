# Actividad 3. Implementación de operaciones con cadenas y lenguajes

**Nombre completo:** Jonathan Hernández Lazcano  
**No. cuenta:** 200417  
**Nombre de la actividad:** Actividad 3. Implementación de operaciones con cadenas y lenguajes

## Descripción

API construida con FastAPI que expone operaciones sobre **cadenas** (concatenación, unión y
potencia) y sobre **lenguajes**, entendidos como conjuntos de cadenas (unión, intersección,
diferencia, concatenación, complemento y clausura de Kleene).

Un lenguaje se representa como una **lista de cadenas** y la cadena vacía λ como `""`. Todas las
operaciones sobre lenguajes trabajan internamente con conjuntos, así que los duplicados se
eliminan, y devuelven el resultado en **orden shortlex**: primero por longitud y, a igual
longitud, en orden alfabético. Ese orden es el que hace que "los primeros N elementos" de una
clausura de Kleene sea una respuesta bien definida.

## Estructura

```
Actividad3-Operaciones-Cadenas-Lenguajes/
├── main.py                  # Crea la app de FastAPI y monta los routers
├── core/
│   ├── cadenas_ops.py       # Operaciones sobre cadenas
│   └── lenguajes_ops.py     # Operaciones sobre lenguajes (+ orden shortlex)
├── routers/
│   ├── cadenas.py           # Endpoints /cadenas/* y sus modelos de petición
│   └── lenguajes.py         # Endpoints /lenguajes/* y sus modelos de petición
├── notebooks/
│   └── ejercicios.ipynb     # Desarrollo de los ejercicios llamando a la API
└── requirements.txt
```

La lógica de `core/` no depende de FastAPI, por eso puede usarse igual desde los endpoints que
directamente desde el notebook.

## Cómo ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Levantar la API (documentación interactiva en http://127.0.0.1:8000/docs)
uvicorn main:app --reload

# Ejecutar el notebook con el desarrollo de los ejercicios
jupyter nbconvert --execute --to notebook --inplace notebooks/ejercicios.ipynb
# o abrirlo interactivamente:
jupyter notebook notebooks/ejercicios.ipynb
```

Con la API levantada, `/docs` ofrece la interfaz de Swagger para probar cada endpoint sin
escribir código. El notebook no necesita el servidor: usa el `TestClient` de FastAPI, que llama
a los mismos endpoints en memoria.

## Endpoints

| Endpoint | Descripción |
|---|---|
| `GET /` | Verificación de estado de la API |

### Cadenas

| Endpoint | Body | Descripción |
|---|---|---|
| `POST /cadenas/concatenar` | `{a, b}` | Concatena dos cadenas |
| `POST /cadenas/unir` | `{cadenas: [...]}` | Concatena una lista de cadenas en orden |
| `POST /cadenas/potencia` | `{cadena, n}` | Repite una cadena n veces (wⁿ); `n = 0` da λ |

### Lenguajes

| Endpoint | Body | Descripción |
|---|---|---|
| `POST /lenguajes/union` | `{L, M}` | L ∪ M |
| `POST /lenguajes/interseccion` | `{L, M}` | L ∩ M |
| `POST /lenguajes/diferencia` | `{L, M}` | L − M |
| `POST /lenguajes/concatenacion` | `{L, M}` | L.M (también sirve para L², usando L=M) |
| `POST /lenguajes/complemento` | `{L, alfabeto, max_length}` | (Σ* hasta max_length) − L |
| `POST /lenguajes/clausura_kleene` | `{L, max_elementos}` | Primeros N elementos de L*, en orden shortlex |

### Formato de la respuesta

Todos los endpoints responden con una sola clave, `resultado`: una cadena en `/cadenas/*` y una
lista de cadenas en `/lenguajes/*`.

```jsonc
// POST /lenguajes/union  →  { "L": ["", "a", "b"], "M": ["b", "aa"] }
{ "resultado": ["", "a", "b", "aa"] }
```

Dos operaciones necesitan un límite explícito, porque su resultado puede ser infinito:

- **Complemento:** Σ* es infinito, así que `max_length` acota el universo a las cadenas de
  longitud ≤ *max_length* (incluida λ) antes de restarle L.
- **Clausura de Kleene:** `max_elementos` (8 por omisión) indica cuántos elementos de L* se
  devuelven. La generación es por capas, según el número de concatenaciones, y solo se detiene
  cuando ninguna capa posterior puede producir una cadena más corta que las ya seleccionadas;
  así los N elementos devueltos son realmente los N primeros en orden shortlex, aunque L mezcle
  cadenas de distinta longitud.

## Ejercicios

Dado el alfabeto Σ = {a, b} y los lenguajes:

- **L** = {λ, 'a', 'b'}  →  `["", "a", "b"]`
- **M** = {'b', 'aa'}  →  `["b", "aa"]`

Los resultados de esta sección son la salida literal de los endpoints; el desarrollo completo,
paso a paso, está en [`notebooks/ejercicios.ipynb`](notebooks/ejercicios.ipynb).

### Operaciones de conjuntos

Se aplican sobre los lenguajes como conjuntos de cadenas, sin mirar el contenido de cada cadena.

| Operación | Petición | Resultado |
|---|---|---|
| L ∪ M | `POST /lenguajes/union` `{"L": L, "M": M}` | {λ, 'a', 'b', 'aa'} |
| L ∩ M | `POST /lenguajes/interseccion` `{"L": L, "M": M}` | {'b'} |
| L − M | `POST /lenguajes/diferencia` `{"L": L, "M": M}` | {λ, 'a'} |
| M − L | `POST /lenguajes/diferencia` `{"L": M, "M": L}` | {'aa'} |

La diferencia no es conmutativa: L − M y M − L dan resultados distintos porque solo `'b'` es
común a los dos lenguajes.

### Operaciones sobre cadenas (concatenación de lenguajes)

L.M es el conjunto de todas las concatenaciones `l + m` con l ∈ L y m ∈ M. Se generan |L| × |M|
cadenas, pero el resultado puede tener menos elementos si alguna se repite.

| Operación | Petición | Resultado |
|---|---|---|
| L.M | `POST /lenguajes/concatenacion` `{"L": L, "M": M}` | {'b', 'aa', 'ab', 'bb', 'aaa', 'baa'} |
| M.L | `POST /lenguajes/concatenacion` `{"L": M, "M": L}` | {'b', 'aa', 'ba', 'bb', 'aaa', 'aab'} |
| M² | `POST /lenguajes/concatenacion` `{"L": M, "M": M}` | {'bb', 'aab', 'baa', 'aaaa'} |

Como λ ∈ L, al concatenar L con M reaparecen los elementos de M sin cambios (`'b'` y `'aa'`).
La concatenación tampoco es conmutativa: L.M ≠ M.L.

### Clausura de Kleene y combinación

L* es el conjunto de todas las concatenaciones de cero o más elementos de L, así que siempre
contiene λ y, salvo casos triviales, es infinito: por eso se piden solo los primeros 8 elementos.

| Operación | Petición | Resultado |
|---|---|---|
| L* (primeros 8 elementos) | `POST /lenguajes/clausura_kleene` `{"L": L, "max_elementos": 8}` | {λ, 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa'} |
| M* (primeros 8 elementos) | `POST /lenguajes/clausura_kleene` `{"L": M, "max_elementos": 8}` | {λ, 'b', 'aa', 'bb', 'aab', 'baa', 'bbb', 'aaaa'} |

Como L = {λ, 'a', 'b'} contiene todos los símbolos de Σ, L* es exactamente Σ*: los 8 primeros
elementos son las cadenas más cortas sobre {a, b}. M*, en cambio, solo genera cadenas formadas
por bloques `'b'` y `'aa'`.

**(LM) ∪ (M\* ∩ L²)** se resuelve en tres pasos encadenados:

| Paso | Petición | Resultado |
|---|---|---|
| L² = L.L | `POST /lenguajes/concatenacion` `{"L": L, "M": L}` | {λ, 'a', 'b', 'aa', 'ab', 'ba', 'bb'} |
| M* ∩ L² | `POST /lenguajes/interseccion` `{"L": M*, "M": L²}` | {λ, 'b', 'aa', 'bb'} |
| (LM) ∪ (M* ∩ L²) | `POST /lenguajes/union` `{"L": LM, "M": M* ∩ L²}` | {λ, 'b', 'aa', 'ab', 'bb', 'aaa', 'baa'} |

### Resumen

| Operación | Resultado |
|---|---|
| L ∪ M | {λ, 'a', 'b', 'aa'} |
| L ∩ M | {'b'} |
| L − M | {λ, 'a'} |
| M − L | {'aa'} |
| L.M | {'b', 'aa', 'ab', 'bb', 'aaa', 'baa'} |
| M.L | {'b', 'aa', 'ba', 'bb', 'aaa', 'aab'} |
| M² | {'bb', 'aab', 'baa', 'aaaa'} |
| L* (8 elementos) | {λ, 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa'} |
| M* (8 elementos) | {λ, 'b', 'aa', 'bb', 'aab', 'baa', 'bbb', 'aaaa'} |
| (LM) ∪ (M* ∩ L²) | {λ, 'b', 'aa', 'ab', 'bb', 'aaa', 'baa'} |
