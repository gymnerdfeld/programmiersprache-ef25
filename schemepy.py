#  ____       _                                     
# / ___|  ___| |__   ___ _ __ ___   ___ _ __  _   _ 
# \___ \ / __| '_ \ / _ \ '_ ` _ \ / _ \ '_ \| | | |
#  ___) | (__| | | |  __/ | | | | |  __/ |_) | |_| |
# |____/ \___|_| |_|\___|_| |_| |_|\___| .__/ \__, |
#                                      |_|    |___/ 

def tokenize(source_code):
    return source_code.replace("(", " ( ").replace(")", " ) ").split()

def parse(tokens):
    token = tokens.pop(0)
    if token == '(':
        lst = []
        while tokens[0] != ')':
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

def plus(a, b):
    return a + b

def minus(a, b):
    return a - b

def mult(a, b):
    return a * b


def begin(*args):
    return args[-1]

import random

builtins = {
    "+": plus,
    "-": minus, 
    "*": mult,
    "e": 2.718281828459045,
    "random": random.random,
    "begin": begin,
}

library = """
(begin
    (sto quadrieren (func (x)
        (* x x)
    ))
    (sto pi 3.141592653589793)
)
"""

stack = [builtins, {}]   # Stack wächst in diese Richtung ->
#                  ^
#                  |
#                Globale Variablen
    


def evaluate(expr):
    match expr:
        ##################
        # Einfache Werte #
        ##################
        case int(x) | float(x):     # Zahl
            return x

        case str(name):             # Name
            for scope in reversed(stack):
                if name in scope:
                    return scope[name]
            raise NameError(f"name '{name}' is not defined")

        #####################
        # Spezialkonstrukte #
        #####################
        case ["sto", name, value]:    # Einen Wert unter einem Namen abspeichern
            scope = stack[-1]
            scope[name] = evaluate(value)

        case ["if", condition, body_true, body_false]:
            if evaluate(condition):
                return evaluate(body_true)
            else:
                return evaluate(body_false)

        case ["func", params, body]:  # Funktionsdefinition
            return ["func", params, body]


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
                case ["func", params, body]:    # Schemepy Funktion
                    # FIXME
                    # 1. Neuer Scope erstellen

                    local_scope = {}
                    stack.append(local_scope)

                    # 2. Parameter abspeichern (in neuem Scope)
                    for name, value in zip(params, evaluated_args):
                        local_scope[name] = value
                    # 3. Funktion ausführen
                    result = evaluate(body)
                    # 4. Scope wieder löschen
                    stack.pop()
                    return result
                case _:                         # In Python geschriebene Funktion
                    return func(*evaluated_args)
        case _:
            raise ValueError("Invalid expression")


###########
# Helpers #
###########
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