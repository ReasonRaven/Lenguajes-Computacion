"""Análisis estático de la complejidad temporal de un programa escrito en Python.

El programa se recorre con el módulo `ast`. Cada sentencia recibe un costo igual a
(número de veces que se ejecuta) × (costo propio), y con esos costos se arma un
archivo anotado línea por línea y un resumen por función y del programa completo.

Se analizan dos casos:
- PEOR caso (Big-O): se toma siempre el camino más costoso.
- MEJOR caso (Big-Ω): los ciclos con `return`/`break` pueden terminar en la primera
  iteración, de un `if/else` se toma la rama más barata y las validaciones de entrada
  al inicio de una función (`if n < 0: return None`) se ignoran.
"""

import ast
import math
import re
from collections import Counter
from dataclasses import dataclass, field

PEOR = "peor"
MEJOR = "mejor"

MODULO = "<módulo>"

_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


class ProgramaInvalido(ValueError):
    """El contenido recibido no es un programa de Python válido."""


@dataclass(frozen=True, order=True)
class Complejidad:
    """Término de la forma 2^(exp·n) · n^n · log^log(n).

    El orden de los campos define el orden de crecimiento: exponencial, después
    potencia de n y por último potencia del logaritmo."""

    exp: int = 0
    n: int = 0
    log: int = 0

    def __mul__(self, otra: "Complejidad") -> "Complejidad":
        return Complejidad(max(self.exp, otra.exp), self.n + otra.n, self.log + otra.log)

    def __str__(self) -> str:
        partes = []
        if self.n:
            partes.append("n" if self.n == 1 else f"n{str(self.n).translate(_SUPERINDICES)}")
        if self.log:
            partes.append(
                "log n" if self.log == 1 else f"log{str(self.log).translate(_SUPERINDICES)} n"
            )
        texto = " ".join(partes)
        if self.exp:
            return f"{texto}·2ⁿ" if texto else "2ⁿ"
        return texto or "1"


UNO = Complejidad()
LOG = Complejidad(log=1)
N = Complejidad(n=1)
NLOGN = Complejidad(n=1, log=1)
EXP = Complejidad(exp=1)

# Funciones integradas: nombre -> (costo en el peor caso, costo en el mejor caso).
# Solo aplican cuando reciben una colección (un único argumento).
_INTEGRADAS = {
    "sorted": (NLOGN, NLOGN),
    "sum": (N, N),
    "min": (N, N),
    "max": (N, N),
    "list": (N, N),
    "tuple": (N, N),
    "set": (N, N),
    "frozenset": (N, N),
    "dict": (N, N),
    "any": (N, UNO),
    "all": (N, UNO),
}

# Métodos de listas y cadenas: nombre -> (peor caso, mejor caso).
_METODOS = {
    "sort": (NLOGN, NLOGN),
    "index": (N, UNO),
    "find": (N, UNO),
    "remove": (N, UNO),
    "insert": (N, UNO),
    "count": (N, N),
    "extend": (N, N),
    "copy": (N, N),
    "reverse": (N, N),
    "join": (N, N),
    "split": (N, N),
    "replace": (N, N),
}

_DIVISORES = (ast.FloorDiv, ast.Div, ast.RShift)
_MULTIPLICADORES = (ast.Mult, ast.LShift)
_DEFINICIONES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)

NOTA_GUARDA = "validación / caso base: no cuenta en el mejor caso"
NOTA_RAMA = "rama más costosa: no cuenta en el mejor caso"
NOTA_SALIDA = "puede terminar en la primera iteración (return/break)"


def notacion(costo: Complejidad, caso: str) -> str:
    return f"{'O' if caso == PEOR else 'Ω'}({costo})"


@dataclass
class _Linea:
    costo: Complejidad
    considerada: bool = True
    nota: str | None = None


@dataclass
class _Ambito:
    """Una función (o el código suelto del módulo) con el costo de cada línea."""

    nombre: str
    nodo: ast.FunctionDef | ast.AsyncFunctionDef | None
    lineas: dict[int, _Linea] = field(default_factory=dict)
    lineas_recursivas: set[int] = field(default_factory=set)
    total: Complejidad = UNO
    recurrencia: str | None = None

    @property
    def nombre_simple(self) -> str:
        return self.nombre.rsplit(".", 1)[-1]


class _Analizador:
    def __init__(self, codigo: str, caso: str):
        if caso not in (PEOR, MEJOR):
            raise ValueError(f"Caso desconocido: {caso}")
        try:
            self.arbol = ast.parse(codigo)
        except SyntaxError as error:
            raise ProgramaInvalido(
                f"El archivo no es un programa de Python válido: {error.msg} (línea {error.lineno})."
            ) from error
        self.caso = caso
        self.fuente = codigo.splitlines()
        # nombre simple -> nombre completo ("Clase.metodo" para métodos)
        self.funciones: dict[str, str] = {}
        self.nodos: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.orden: list[str] = []
        self.ambitos: dict[str, _Ambito] = {}
        self.en_proceso: set[str] = set()
        self._registrar_funciones(self.arbol.body, prefijo="")

    # ------------------------------------------------------------------ registro

    def _registrar_funciones(self, sentencias: list[ast.stmt], prefijo: str) -> None:
        for sentencia in sentencias:
            if isinstance(sentencia, (ast.FunctionDef, ast.AsyncFunctionDef)):
                completo = f"{prefijo}{sentencia.name}"
                self.funciones.setdefault(sentencia.name, completo)
                self.funciones[completo] = completo
                self.nodos[completo] = sentencia
                self.orden.append(completo)
            elif isinstance(sentencia, ast.ClassDef):
                self._registrar_funciones(sentencia.body, prefijo=f"{prefijo}{sentencia.name}.")

    # ------------------------------------------------------------------ ámbitos

    def analizar(self) -> list[_Ambito]:
        resultado = [self._ambito_funcion(nombre) for nombre in self.orden]

        sueltas = [
            s
            for s in self.arbol.body
            if not isinstance(s, (*_DEFINICIONES, ast.Import, ast.ImportFrom))
            and not _es_docstring(s)
        ]
        if sueltas:
            modulo = _Ambito(MODULO, None)
            self._bloque(sueltas, UNO, modulo)
            modulo.total = _maximo(modulo)
            resultado.append(modulo)
        return resultado

    def _ambito_funcion(self, nombre: str) -> _Ambito:
        if nombre in self.ambitos:
            return self.ambitos[nombre]

        nodo = self.nodos[nombre]
        ambito = _Ambito(nombre, nodo)
        self.en_proceso.add(nombre)
        self._bloque(nodo.body, UNO, ambito, nivel_funcion=True)
        self.en_proceso.discard(nombre)

        ambito.total = _maximo(ambito)
        self._aplicar_recursion(ambito)
        self.ambitos[nombre] = ambito
        return ambito

    def _aplicar_recursion(self, ambito: _Ambito) -> None:
        """Si la función se llama a sí misma, resuelve la recurrencia y asigna el
        resultado a la(s) línea(s) que contienen la llamada recursiva."""
        llamadas = [n for n in ast.walk(ambito.nodo) if self._es_llamada_propia(n, ambito)]
        if not llamadas or not ambito.lineas_recursivas:
            return

        a = len(llamadas)
        por_llamada = ambito.total
        divide = any(_divide(arg) for llamada in llamadas for arg in llamada.args) or bool(
            _variables_que_dividen(ambito.nodo.body)
        )

        if divide:
            critico = math.log2(a)
            d = por_llamada.n
            if d > critico:
                total = por_llamada
            elif d == critico:
                total = por_llamada * LOG
            else:
                total = Complejidad(n=math.ceil(critico))
            llamada_texto = "T(n/2)"
        else:
            total = por_llamada * (N if a == 1 else EXP)
            llamada_texto = "T(n-1)"

        coeficiente = "" if a == 1 else str(a)
        ambito.recurrencia = (
            f"T(n) = {coeficiente}{llamada_texto} + {notacion(por_llamada, self.caso)}"
            f"  ⇒  {notacion(total, self.caso)}"
        )
        for linea in ambito.lineas_recursivas:
            entrada = ambito.lineas[linea]
            entrada.costo = max(entrada.costo, total)
            if entrada.considerada:
                entrada.nota = f"llamada recursiva: {ambito.recurrencia}"
        ambito.total = max(ambito.total, total)

    # ------------------------------------------------------------------ sentencias

    def _bloque(
        self,
        sentencias: list[ast.stmt],
        mult: Complejidad,
        ambito: _Ambito,
        nivel_funcion: bool = False,
    ) -> tuple[Complejidad, set[int]]:
        """Recorre una secuencia de sentencias que se ejecutan `mult` veces.

        Devuelve el costo del bloque (el término dominante de la suma) y las
        líneas que se anotaron."""
        costo = mult
        tocadas: set[int] = set()
        for sentencia in sentencias:
            c, t = self._sentencia(sentencia, mult, ambito, nivel_funcion)
            costo = max(costo, c)
            tocadas |= t
        return costo, tocadas

    def _sentencia(
        self, s: ast.stmt, mult: Complejidad, ambito: _Ambito, nivel_funcion: bool
    ) -> tuple[Complejidad, set[int]]:
        if _es_docstring(s) or isinstance(s, (*_DEFINICIONES, ast.Import, ast.ImportFrom)):
            return mult, set()

        if isinstance(s, ast.If):
            return self._si(s, mult, ambito, nivel_funcion)
        if isinstance(s, (ast.For, ast.AsyncFor)):
            return self._ciclo(s, mult, ambito, self._iteraciones_for(s.iter), s.iter)
        if isinstance(s, ast.While):
            return self._ciclo(s, mult, ambito, self._iteraciones_while(s), s.test)

        if isinstance(s, (ast.With, ast.AsyncWith)):
            linea = self._linea_encabezado(s)
            costo = mult
            for item in s.items:
                costo = max(costo, mult * self._costo_expr(item.context_expr, ambito))
                self._anotar(ambito, linea, costo, item.context_expr)
            c, t = self._bloque(s.body, mult, ambito)
            return max(costo, c), t | {linea}

        if isinstance(s, ast.Try) or type(s).__name__ == "TryStar":
            costo, tocadas = mult, set()
            bloques = [s.body, s.orelse, s.finalbody, *(h.body for h in s.handlers)]
            for bloque in bloques:
                c, t = self._bloque(bloque, mult, ambito)
                costo, tocadas = max(costo, c), tocadas | t
            return costo, tocadas

        if isinstance(s, ast.Match):
            linea = self._linea_encabezado(s)
            costo = mult * self._costo_expr(s.subject, ambito)
            self._anotar(ambito, linea, costo, s.subject)
            tocadas = {linea}
            for caso in s.cases:
                c, t = self._bloque(caso.body, mult, ambito)
                costo, tocadas = max(costo, c), tocadas | t
            return costo, tocadas

        # Sentencia simple: asignación, return, expresión, etc.
        linea = s.end_lineno or s.lineno
        costo = mult * self._costo_expr(s, ambito)
        self._anotar(ambito, linea, costo, s)
        return costo, {linea}

    def _si(
        self, s: ast.If, mult: Complejidad, ambito: _Ambito, nivel_funcion: bool
    ) -> tuple[Complejidad, set[int]]:
        linea = self._linea_encabezado(s)
        costo_condicion = mult * self._costo_expr(s.test, ambito)
        self._anotar(ambito, linea, costo_condicion, s.test)

        if self.caso == MEJOR and nivel_funcion and _es_guarda(s):
            _, tocadas = self._bloque(s.body, mult, ambito)
            tocadas.add(linea)
            self._descartar(ambito, tocadas, NOTA_GUARDA)
            return UNO, tocadas

        costo_si, tocadas_si = self._bloque(s.body, mult, ambito)
        if s.orelse:
            costo_no, tocadas_no = self._bloque(s.orelse, mult, ambito)
        else:
            costo_no, tocadas_no = mult, set()

        if self.caso == MEJOR and costo_si != costo_no:
            self._descartar(ambito, tocadas_si if costo_si > costo_no else tocadas_no, NOTA_RAMA)
            rama = min(costo_si, costo_no)
        else:
            rama = max(costo_si, costo_no)
        return max(costo_condicion, rama), {linea} | tocadas_si | tocadas_no

    def _ciclo(
        self,
        s: ast.For | ast.AsyncFor | ast.While,
        mult: Complejidad,
        ambito: _Ambito,
        iteraciones: Complejidad,
        encabezado: ast.expr,
    ) -> tuple[Complejidad, set[int]]:
        nota = None
        if self.caso == MEJOR and _tiene_salida_temprana(s.body):
            iteraciones, nota = UNO, NOTA_SALIDA

        linea = self._linea_encabezado(s)
        costo_encabezado = mult * iteraciones * self._costo_expr(encabezado, ambito)
        self._anotar(ambito, linea, costo_encabezado, encabezado, nota)

        costo_cuerpo, tocadas = self._bloque(s.body, mult * iteraciones, ambito)
        costo_else, tocadas_else = self._bloque(s.orelse, mult, ambito)
        return max(costo_encabezado, costo_cuerpo, costo_else), {linea} | tocadas | tocadas_else

    # ------------------------------------------------------------------ ciclos

    @staticmethod
    def _iteraciones_for(iterable: ast.expr) -> Complejidad:
        """Un `for` sobre un rango o literal de constantes es O(1); sobre cualquier
        cosa que dependa de la entrada (range(n), una lista, etc.) es O(n)."""
        if isinstance(iterable, ast.Call) and _nombre(iterable.func) == "range":
            return UNO if all(_es_constante(arg) for arg in iterable.args) else N
        if isinstance(iterable, (ast.List, ast.Tuple, ast.Set, ast.Constant)):
            return UNO if _es_constante(iterable) else N
        return N

    @staticmethod
    def _iteraciones_while(s: ast.While) -> Complejidad:
        """Un `while` es O(log n) si alguna variable de su condición se divide o
        multiplica por una constante en cada vuelta (directa o indirectamente, como
        `medio = (izq + der) // 2; izq = medio + 1`). Si no, se supone O(n)."""
        variables_condicion = _nombres(s.test)
        if variables_condicion & _variables_que_dividen(s.body):
            return LOG
        return N

    # ------------------------------------------------------------------ expresiones

    def _costo_expr(self, nodo: ast.AST, ambito: _Ambito) -> Complejidad:
        """Costo de evaluar una expresión una sola vez."""
        if isinstance(nodo, _DEFINICIONES):
            return UNO

        if isinstance(nodo, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            elementos = [nodo.key, nodo.value] if isinstance(nodo, ast.DictComp) else [nodo.elt]
            costo = UNO
            for parte in elementos + [c for g in nodo.generators for c in g.ifs]:
                costo = max(costo, self._costo_expr(parte, ambito))
            for generador in nodo.generators:
                costo = costo * self._iteraciones_for(generador.iter)
                costo = max(costo, self._costo_expr(generador.iter, ambito))
            return costo

        costo = UNO
        for hijo in ast.iter_child_nodes(nodo):
            costo = max(costo, self._costo_expr(hijo, ambito))

        if isinstance(nodo, ast.Call):
            costo = max(costo, self._costo_llamada(nodo, ambito))
        elif isinstance(nodo, ast.Compare) and self.caso == PEOR:
            busquedas = [
                comparado
                for op, comparado in zip(nodo.ops, nodo.comparators)
                if isinstance(op, (ast.In, ast.NotIn))
            ]
            if any(not _es_constante(c) for c in busquedas):
                costo = max(costo, N)
        return costo

    def _costo_llamada(self, llamada: ast.Call, ambito: _Ambito) -> Complejidad:
        funcion = llamada.func
        indice = 0 if self.caso == PEOR else 1

        if isinstance(funcion, ast.Name):
            if funcion.id in self.funciones:
                return self._costo_usuario(funcion.id, ambito)
            if funcion.id in _INTEGRADAS and len(llamada.args) == 1:
                return _INTEGRADAS[funcion.id][indice]
            return UNO

        if isinstance(funcion, ast.Attribute):
            receptor = funcion.value
            if (
                isinstance(receptor, ast.Name)
                and receptor.id in ("self", "cls")
                and funcion.attr in self.funciones
            ):
                return self._costo_usuario(funcion.attr, ambito)
            if funcion.attr in _METODOS:
                return _METODOS[funcion.attr][indice]
        return UNO

    def _costo_usuario(self, nombre: str, ambito: _Ambito) -> Complejidad:
        completo = self.funciones[nombre]
        if completo == ambito.nombre or completo in self.en_proceso:
            # La recursión directa se resuelve al terminar la función.
            return UNO
        return self._ambito_funcion(completo).total

    # ------------------------------------------------------------------ utilidades

    def _es_llamada_propia(self, nodo: ast.AST, ambito: _Ambito) -> bool:
        if ambito.nodo is None or not isinstance(nodo, ast.Call):
            return False
        funcion = nodo.func
        if isinstance(funcion, ast.Name):
            return self.funciones.get(funcion.id) == ambito.nombre
        return (
            isinstance(funcion, ast.Attribute)
            and isinstance(funcion.value, ast.Name)
            and funcion.value.id in ("self", "cls")
            and funcion.attr == ambito.nombre_simple
        )

    def _anotar(
        self,
        ambito: _Ambito,
        linea: int,
        costo: Complejidad,
        nodo: ast.AST,
        nota: str | None = None,
    ) -> None:
        if any(self._es_llamada_propia(n, ambito) for n in ast.walk(nodo)):
            ambito.lineas_recursivas.add(linea)

        existente = ambito.lineas.get(linea)
        if existente is None:
            ambito.lineas[linea] = _Linea(costo, nota=nota)
        else:
            # Varias sentencias en la misma línea física: domina la mayor.
            existente.costo = max(existente.costo, costo)
            existente.nota = existente.nota or nota

    @staticmethod
    def _descartar(ambito: _Ambito, lineas: set[int], nota: str) -> None:
        for linea in lineas:
            entrada = ambito.lineas[linea]
            entrada.considerada = False
            entrada.nota = nota

    def _linea_encabezado(self, s: ast.stmt) -> int:
        """Última línea física del encabezado de una sentencia compuesta (la que
        termina en `:`), que es donde se puede añadir un comentario."""
        primera_del_cuerpo = s.body[0].lineno if s.body else s.lineno
        if primera_del_cuerpo <= s.lineno:
            return s.lineno
        for linea in range(primera_del_cuerpo - 1, s.lineno - 1, -1):
            texto = self.fuente[linea - 1].strip()
            if texto and not texto.startswith("#"):
                return linea
        return s.lineno


# ---------------------------------------------------------------------- helpers


def _maximo(ambito: _Ambito) -> Complejidad:
    return max((e.costo for e in ambito.lineas.values() if e.considerada), default=UNO)


def _es_docstring(s: ast.stmt) -> bool:
    return (
        isinstance(s, ast.Expr)
        and isinstance(s.value, ast.Constant)
        and isinstance(s.value.value, str)
    )


def _es_guarda(s: ast.If) -> bool:
    """`if <condición>: return/raise` sin `else` ni ciclos: validación de entrada
    o caso base de una recursión."""
    return (
        not s.orelse
        and isinstance(s.body[-1], (ast.Return, ast.Raise))
        and not any(isinstance(n, (ast.For, ast.AsyncFor, ast.While)) for n in ast.walk(s))
    )


def _tiene_salida_temprana(cuerpo: list[ast.stmt]) -> bool:
    """¿El cuerpo de un ciclo contiene un `return`, o un `break` que salga de ese
    mismo ciclo (no de uno anidado)?"""

    def buscar(nodo: ast.AST, en_ciclo_anidado: bool) -> bool:
        if isinstance(nodo, ast.Return):
            return True
        if isinstance(nodo, ast.Break) and not en_ciclo_anidado:
            return True
        if isinstance(nodo, _DEFINICIONES):
            return False
        anidado = en_ciclo_anidado or isinstance(nodo, (ast.For, ast.AsyncFor, ast.While))
        return any(buscar(hijo, anidado) for hijo in ast.iter_child_nodes(nodo))

    return any(buscar(s, False) for s in cuerpo)


def _es_numero_mayor_que_uno(nodo: ast.AST) -> bool:
    return (
        isinstance(nodo, ast.Constant)
        and isinstance(nodo.value, (int, float))
        and not isinstance(nodo.value, bool)
        and nodo.value >= 2
    )


def _divide(expr: ast.AST) -> bool:
    """¿La expresión divide o multiplica algo por una constante ≥ 2?"""
    for nodo in ast.walk(expr):
        if not isinstance(nodo, ast.BinOp):
            continue
        if isinstance(nodo.op, _DIVISORES) and _es_numero_mayor_que_uno(nodo.right):
            return True
        if isinstance(nodo.op, _MULTIPLICADORES) and (
            _es_numero_mayor_que_uno(nodo.left) or _es_numero_mayor_que_uno(nodo.right)
        ):
            return True
    return False


def _variables_que_dividen(cuerpo: list[ast.stmt]) -> set[str]:
    """Variables que en el cuerpo se dividen/multiplican por una constante, más las
    que se calculan a partir de ellas (propagación hasta un punto fijo)."""
    asignaciones: list[tuple[set[str], ast.expr]] = []
    divididas: set[str] = set()

    for nodo in (n for s in cuerpo for n in ast.walk(s)):
        if isinstance(nodo, ast.Assign):
            objetivos = set().union(*(_nombres_asignados(t) for t in nodo.targets))
            asignaciones.append((objetivos, nodo.value))
        elif isinstance(nodo, ast.AnnAssign) and nodo.value is not None:
            asignaciones.append((_nombres_asignados(nodo.target), nodo.value))
        elif isinstance(nodo, ast.AugAssign):
            objetivos = _nombres_asignados(nodo.target)
            if isinstance(nodo.op, (*_DIVISORES, *_MULTIPLICADORES)) and _es_numero_mayor_que_uno(
                nodo.value
            ):
                divididas |= objetivos
            asignaciones.append((objetivos, nodo.value))

    for objetivos, valor in asignaciones:
        if _divide(valor):
            divididas |= objetivos

    cambio = True
    while cambio:
        cambio = False
        for objetivos, valor in asignaciones:
            if not objetivos <= divididas and _nombres(valor) & divididas:
                divididas |= objetivos
                cambio = True
    return divididas


def _nombres(expr: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


def _nombres_asignados(objetivo: ast.AST) -> set[str]:
    if isinstance(objetivo, ast.Name):
        return {objetivo.id}
    if isinstance(objetivo, (ast.Tuple, ast.List)):
        return set().union(*(_nombres_asignados(e) for e in objetivo.elts))
    return set()


def _nombre(expr: ast.AST) -> str | None:
    return expr.id if isinstance(expr, ast.Name) else None


def _es_constante(expr: ast.AST) -> bool:
    """La expresión no depende de ninguna variable ni llamada."""
    return not any(
        isinstance(n, (ast.Name, ast.Attribute, ast.Call, ast.Subscript, ast.Starred))
        for n in ast.walk(expr)
    )


# ---------------------------------------------------------------------- salida


def _suma(costos: list[Complejidad], caso: str) -> str:
    return " + ".join(notacion(c, caso) for c in costos) or notacion(UNO, caso)


def _suma_agrupada(costos: list[Complejidad], caso: str) -> str:
    conteo = Counter(costos)
    return (
        " + ".join(f"{conteo[c]}·{notacion(c, caso)}" for c in sorted(conteo))
        or notacion(UNO, caso)
    )


def _envolver(etiqueta: str, texto: str, ancho: int = 92) -> list[str]:
    """Parte una suma larga en varias líneas de comentario, cortando en los `+`."""
    terminos = texto.split(" + ")
    lineas, actual = [], f"# {etiqueta}{terminos[0]}"
    sangria = "# " + " " * len(etiqueta)
    for termino in terminos[1:]:
        if len(actual) + len(termino) + 3 > ancho:
            lineas.append(actual)
            actual = f"{sangria}+ {termino}"
        else:
            actual += f" + {termino}"
    lineas.append(actual)
    return lineas


def _bloque_resumen(resultado: dict) -> list[str]:
    caso = resultado["caso"]
    titulo = (
        "PEOR CASO (notación Big-O)" if caso == PEOR else "MEJOR CASO (notación Big-Omega, Ω)"
    )
    regla = "# " + "=" * 78
    separador = "# " + "-" * 78
    bloque = [
        regla,
        f"# RESUMEN DE COMPLEJIDAD — {titulo}",
        f"# Archivo analizado: {resultado['archivo']}",
        regla,
    ]
    for funcion in resultado["funciones"]:
        bloque += [
            "#",
            f"# {funcion['nombre']}"
            + (f" (línea {funcion['linea']})" if funcion["linea"] else ""),
            *_envolver("  Suma de complejidades : ", funcion["suma"]),
            *_envolver("  Términos agrupados    : ", funcion["suma_agrupada"]),
        ]
        if funcion["recurrencia"]:
            bloque.append(f"#   Recurrencia           : {funcion['recurrencia']}")
        bloque.append(f"#   Mayor grado           : {funcion['complejidad']}")

    programa = resultado["programa"]
    bloque += [
        "#",
        separador,
        "# PROGRAMA COMPLETO",
        *_envolver("  Suma de complejidades : ", programa["suma"]),
        *_envolver("  Términos agrupados    : ", programa["suma_agrupada"]),
        f"#   Mayor grado           : {programa['complejidad']}"
        + (f"  →  {', '.join(programa['funciones_mayor_grado'])}" if programa["funciones_mayor_grado"] else ""),
    ]
    if caso == MEJOR:
        bloque += [
            "#",
            "# Las líneas marcadas como «no cuenta en el mejor caso» quedan fuera de la suma.",
        ]
    bloque.append(regla)
    return bloque


def _anotar_archivo(codigo: str, ambitos: list[_Ambito], resultado: dict, analizador: _Analizador) -> str:
    caso = resultado["caso"]
    comentarios: dict[int, str] = {}

    for ambito in ambitos:
        if ambito.nodo is not None:
            linea_def = analizador._linea_encabezado(ambito.nodo)
            if linea_def not in ambito.lineas:
                comentarios[linea_def] = (
                    f"Complejidad de {ambito.nombre}: {notacion(ambito.total, caso)}"
                )
        for linea, entrada in ambito.lineas.items():
            texto = notacion(entrada.costo, caso)
            if entrada.nota:
                texto += f"  ← {entrada.nota}"
            comentarios[linea] = texto

    lineas = codigo.splitlines()
    anotables = [lineas[i - 1].rstrip() for i in comentarios if i <= len(lineas)]
    columna = min(max((len(l) for l in anotables), default=0) + 2, 80)

    salida = []
    for numero, texto in enumerate(lineas, start=1):
        if numero in comentarios:
            base = texto.rstrip()
            relleno = " " * max(2, columna - len(base))
            salida.append(f"{base}{relleno}# {comentarios[numero]}")
        else:
            salida.append(texto)

    while salida and not salida[-1].strip():
        salida.pop()
    salida += ["", ""] + _bloque_resumen(resultado)
    return "\n".join(salida) + "\n"


def analizar(codigo: str, caso: str, nombre_archivo: str = "programa.py") -> dict:
    """Analiza `codigo` en el caso indicado (`"peor"` o `"mejor"`).

    Devuelve el detalle por función, el resumen del programa y el archivo anotado.
    Lanza `ProgramaInvalido` si el código no es Python válido."""
    analizador = _Analizador(codigo, caso)
    ambitos = analizador.analizar()

    funciones = []
    todos_los_costos: list[Complejidad] = []
    for ambito in ambitos:
        ordenadas = sorted(ambito.lineas.items())
        costos = [e.costo for _, e in ordenadas if e.considerada]
        todos_los_costos += costos
        funciones.append(
            {
                "nombre": ambito.nombre,
                "linea": ambito.nodo.lineno if ambito.nodo else None,
                "lineas": [
                    {
                        "linea": linea,
                        "codigo": analizador.fuente[linea - 1].strip(),
                        "complejidad": notacion(entrada.costo, caso),
                        "cuenta": entrada.considerada,
                        "nota": entrada.nota,
                    }
                    for linea, entrada in ordenadas
                ],
                "suma": _suma(costos, caso),
                "suma_agrupada": _suma_agrupada(costos, caso),
                "recurrencia": ambito.recurrencia,
                "complejidad": notacion(ambito.total, caso),
            }
        )

    totales = [a.total for a in ambitos]
    mayor = max(totales, default=UNO)
    resultado = {
        "archivo": nombre_archivo,
        "caso": caso,
        "notacion": "Big-O" if caso == PEOR else "Big-Omega",
        "funciones": funciones,
        "programa": {
            "suma": _suma(totales, caso),
            "suma_agrupada": _suma_agrupada(todos_los_costos, caso),
            "complejidad": notacion(mayor, caso),
            "funciones_mayor_grado": [a.nombre for a in ambitos if a.total == mayor],
        },
    }
    resultado["archivo_anotado"] = _anotar_archivo(codigo, ambitos, resultado, analizador)
    return resultado


def nombre_salida(nombre_archivo: str, caso: str) -> str:
    """`algoritmos.py` -> `algoritmos_peor_caso.py` (solo caracteres ASCII seguros)."""
    base = re.sub(r"\.[^.]*$", "", nombre_archivo.rsplit("/", 1)[-1]) or "programa"
    base = re.sub(r"[^A-Za-z0-9_-]", "_", base)
    return f"{base}_{caso}_caso.py"
