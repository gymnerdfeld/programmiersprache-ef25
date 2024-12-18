#  ____       _
# / ___|  ___| |__   ___ _ __ ___   ___ _ __  _   _
# \___ \ / __| '_ \ / _ \ '_ ` _ \ / _ \ '_ \| | | |
#  ___) | (__| | | |  __/ | | | | |  __/ |_) | |_| |
# |____/ \___|_| |_|\___|_| |_| |_|\___| .__/ \__, |
#                                      |_|    |___/


def tokenize(source_code):
    source_code = "\n".join(line.split(";")[0] for line in source_code.split("\n"))
    return source_code.replace("(", " ( ").replace(")", " ) ").split()


def parse(tokens):
    token = tokens.pop(0)
    if token == "(":
        lst = []
        while tokens[0] != ")":
            lst.append(parse(tokens))
        tokens.pop(0)
        return lst
    else:
        if token[0] in "0123456789-" and token != "-":
            if "." in token:
                return float(token)
            else:
                return int(token)
        else:
            return token


# ========================================== #
# Builtins                                   #
# ========================================== #

# Math
def plus(a, b):
    return a + b

def minus(a, b):
    return a - b

def mult(a, b):
    return a * b

def exp(a, b):
    return a ** b

def div(a, b):
    return a / b

def int_div(a, b):
    return a // b

def modulo(a, b):
    return  a % b

# Vergleichsoperator
def less_than(a, b):
    return a < b

# Block mit mehreren Anweisungen; gibt das Resultat des letzten Ausdrucks zurück
def begin(*args):
    return args[-1]

# dicts
def dict_new():
    return {}

def dict_in(d, key):
    return key in d

def dict_set(d, key, val):
    d[key] = val

def dict_get(d, key):
    return d[key]


import random

builtins = {
    "+": plus,
    "-": minus,
    "*": mult,
    "**": exp,
    "/": div,
    "//": int_div,
    "%": modulo,
    "<": less_than,
    "begin": begin,
    "dict-new": dict_new,
    "dict-set": dict_set,
    "dict-get": dict_get,
    "dict-in?": dict_in,

    # Direkt "importierte" Funktionen und Werte
    "print": print,
    "random": random.random,
    "True": True,
    "False": False,
}


# ========================================== #
# Library (aus File library.lisp importiert) #
# ========================================== #
from pathlib import Path
library_file = Path(__file__).parent / "library.lisp"
library = "(begin " + library_file.open().read() + ")"


# ============================================ #
# Stack mit den globalen und lokalen Variablen #
# ============================================ #
stack = [builtins, {}]  # Stack wächst in diese Richtung ->
#                  ^
#                  |
#                Globale Variablen


# ============================================ #
# Freie Variablen in Closure finden            #
# ============================================ #
def find_free_vars(expr, params=[]):
    match expr:
        case int(number) | float(number):
            return []
        case str(name):
            if name in params or name in stack[0] or name in stack[1]:
                return []
            else:
                return [name]
        case ["func", ps, body]:
            return find_free_vars(body, params + ps)
        case ["sto", name, expr]:
            params.append(name)
            return find_free_vars(expr, params)
        case ["if", a, b, c]:
            return find_free_vars([a, b, c], params)
        case ["string", *_]:
            return []
        case [*exprs]:
            free_vars = []
            for expr in exprs:
                free_vars.extend(find_free_vars(expr, params))
            return free_vars


# ============================================ #
# Ausdruck evaluieren / ausführen              #
# ============================================ #
def evaluate(expr):
    match expr:
        ##################
        # Einfache Werte #
        ##################
        case int(x) | float(x):  # Zahl
            return x

        case str(name):  # Name
            for scope in reversed(stack):
                if name in scope:
                    return scope[name]
            raise NameError(f"name '{name}' is not defined")

        #####################
        # Spezialkonstrukte #
        #####################

        # Einen Wert unter einem Namen abspeichern
        case ["sto", name, value]:
            scope = stack[-1]
            scope[name] = evaluate(value)

        # Bedingte Ausführung (if)
        case ["if", condition, body_true, body_false]:
            if evaluate(condition):
                return evaluate(body_true)
            else:
                return evaluate(body_false)

        # Funktionsdefinition
        case ["func", params, body]:  # Funktionsdefinition
            names = find_free_vars(body, params)
            return ["func", params, body, names, stack[-1]]

        # String (Mehrere Wörter werden mit Leerzeichen zusammen gesetzt)
        case ["string", *words]:
            return " ".join(words)

        #######################
        # Funktionen anwenden #
        #######################
        case [operator, *args]:
            evaluated_args = []
            func = evaluate(operator)

            for arg in args:
                evaluated_arg = evaluate(arg)
                evaluated_args.append(evaluated_arg)

            # Unterscheide Funktion in Python oder Schemepy
            match func:

                # Schemepy Funktion
                case ["func", params, body, free_var_names, closure]:
                    # 1. Neuer Scope erstellen
                    local_scope = {}
                    # 2a. Closure-Variablen abspeichern (in neuem Scope)
                    for name in free_var_names:
                        local_scope[name] = closure[name]
                    # 2b. Parameter abspeichern (in neuem Scope)
                    for name, value in zip(params, evaluated_args):
                        local_scope[name] = value
                    # 3. Neuer lokaler Scope auf dem Stack abspeichern
                    stack.append(local_scope)
                    # 4. Funktion ausführen
                    result = evaluate(body)
                    # 5. Lokaler Scope der Funktion wieder vom Stack löschen
                    stack.pop()
                    # 6. Berechnetes Resultat zurück geben
                    return result

                # In Python geschriebene Funktion
                case _:
                    return func(*evaluated_args)
        case _:
            raise ValueError("Invalid expression")


# ============================================ #
# Hilfsfunktionen                              #
# ============================================ #
def run(source_code):
    tokens = tokenize(source_code)
    # print(f"Tokens: {tokens}")
    syntax_tree = parse(tokens)
    # print(f"Syntax Tree: {syntax_tree}")
    result = evaluate(syntax_tree)
    # print(f"Result: {result}")
    return result


def tests():
    # 1 + 1
    assert run("(+ 1 1)") == 2
    # 3 - 2
    assert run("(- 3 2)") == 1
    # 1
    assert run("1") == 1
    # 1.5
    assert run("1.5") == 1.5
    # 2 * 3 + 1
    assert run("(+ (* 2 3) 1)") == 7


def repl():
    print("Welcome to Schemepy. Enter 'q' to exit.")

    run(library)

    done = False
    while not done:
        expr = input("> ")
        if expr.strip().lower() == "q":
            done = True
        else:
            try:
                result = run(expr)
                print(result)
            except Exception as e:
                print(f"{e.__class__.__name__}: {str(e)}")


if __name__ == "__main__":
    tests()
    repl()
