import functools


def registry():
    functions = []

    def register(func):
        functions.append(func)
        return func

    return functions, register
