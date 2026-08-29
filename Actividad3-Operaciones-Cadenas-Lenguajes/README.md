# Actividad 3. Implementación de operaciones con cadenas y lenguajes

**Nombre completo:** Jonathan Hernández Lazcano
**No. cuenta:** 200417
**Nombre de la actividad:** Actividad 3. Implementación de operaciones con cadenas y lenguajes

## Descripción

API construida con FastAPI que expone operaciones sobre cadenas y sobre
lenguajes (conjuntos de cadenas)

## Cómo ejecutar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Levantar la API
uvicorn main:app --reload

# Ejecutar el notebook con el desarrollo de los ejercicios
jupyter nbconvert --execute --to notebook --inplace notebooks/ejercicios.ipynb
# o abrirlo interactivamente:
jupyter notebook notebooks/ejercicios.ipynb
```


## Endpoints

### Cadenas

| Endpoint | Body | Descripción |
|---|---|---|
| `POST /cadenas/concatenar` | `{a, b}` | Concatena dos cadenas |
| `POST /cadenas/unir` | `{cadenas: [...]}` | Concatena una lista de cadenas en orden |
| `POST /cadenas/potencia` | `{cadena, n}` | Repite una cadena n veces (w^n) |

### Lenguajes

Un lenguaje se representa como una lista de cadenas (λ como `""`).

| Endpoint | Body | Descripción |
|---|---|---|
| `POST /lenguajes/union` | `{L, M}` | L ∪ M |
| `POST /lenguajes/interseccion` | `{L, M}` | L ∩ M |
| `POST /lenguajes/diferencia` | `{L, M}` | L − M |
| `POST /lenguajes/concatenacion` | `{L, M}` | L.M (también sirve para L², usando L=M) |
| `POST /lenguajes/complemento` | `{L, alfabeto, max_length}` | (Σ* hasta max_length) − L |
| `POST /lenguajes/clausura_kleene` | `{L, max_elementos}` | Primeros N elementos de L*, en orden shortlex |

## Ejercicios

Dado el alfabeto Σ={a,b} y los lenguajes:

- L = {λ, 'a', 'b'}
- M = {'b', 'aa'}

### Operaciones de conjuntos

| Operación | Resultado |
|---|---|
| L ∪ M | {λ, 'a', 'b', 'aa'} |
| L ∩ M | {'b'} |
| L − M | {λ, 'a'} |
| M − L | {'aa'} |

### Operaciones sobre cadenas (concatenación de lenguajes)

| Operación | Resultado |
|---|---|
| L.M | {'b', 'aa', 'ab', 'bb', 'aaa', 'baa'} |
| M.L | {'b', 'aa', 'ba', 'bb', 'aaa', 'aab'} |
| M² | {'bb', 'aab', 'baa', 'aaaa'} |

### Clausura de Kleene y combinación

| Operación | Resultado |
|---|---|
| L* (primeros 8 elementos) | {λ, 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa'} |
| M* (primeros 8 elementos) | {λ, 'b', 'aa', 'bb', 'aab', 'baa', 'bbb', 'aaaa'} |
| (LM) ∪ (M* ∩ L²) | {λ, 'b', 'aa', 'ab', 'bb', 'aaa', 'baa'} |
