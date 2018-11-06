"""
The entry point for running on top of python.

"""
from lox.targetpylox import runFile, repl

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        runFile(filename=sys.argv[1])
    else:
        repl(sys.stdin, sys.stdout)
