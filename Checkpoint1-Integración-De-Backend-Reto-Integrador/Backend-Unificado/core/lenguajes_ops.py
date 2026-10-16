from itertools import product


def ordenar(lenguaje: set[str]) -> list[str]:
    return sorted(lenguaje, key=lambda w: (len(w), w))


def union(L: list[str], M: list[str]) -> list[str]:
    return ordenar(set(L) | set(M))


def interseccion(L: list[str], M: list[str]) -> list[str]:
    return ordenar(set(L) & set(M))


def diferencia(L: list[str], M: list[str]) -> list[str]:
    return ordenar(set(L) - set(M))


def concatenacion(L: list[str], M: list[str]) -> list[str]:
    return ordenar({l + m for l in L for m in M})


def complemento(L: list[str], alfabeto: list[str], max_length: int) -> list[str]:
    universo: set[str] = {""}
    for longitud in range(1, max_length + 1):
        for combinacion in product(alfabeto, repeat=longitud):
            universo.add("".join(combinacion))
    return ordenar(universo - set(L))


def clausura_kleene(L: list[str], max_elementos: int) -> list[str]:
    """BFS por número de concatenaciones. Antes de detenerse, verifica que
    ninguna cadena más corta pueda seguir apareciendo en capas futuras, para
    que 'los primeros max_elementos elementos' sea correcto en orden shortlex
    incluso si L mezcla elementos de distinta longitud."""
    min_len = min((len(w) for w in L if w), default=0)
    resultado: set[str] = {""}
    frontera = {""}
    layer = 0
    while frontera:
        if len(resultado) >= max_elementos:
            top_n = ordenar(resultado)[:max_elementos]
            max_len_top_n = len(top_n[-1])
            if min_len == 0 or min_len * (layer + 1) > max_len_top_n:
                break
        nueva_frontera: set[str] = set()
        for w in frontera:
            for l in L:
                if not l:
                    continue
                candidata = w + l
                if candidata not in resultado:
                    nueva_frontera.add(candidata)
        if not nueva_frontera:
            break
        resultado |= nueva_frontera
        frontera = nueva_frontera
        layer += 1
    return ordenar(resultado)[:max_elementos]
