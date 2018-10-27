"""


"""
from lox import Chunk, OpCode
from rpython.rlib import rfile
import os

def debug(msg):
    print "debug:", msg


def repl(stream):
    while True:
        next_line = stream.readline()
        if not next_line:
            break
        print "^" + next_line


def runFile(filename):
    debug("runFile called with: " + filename)

    try:
        file = rfile.create_file(filename, 'r')
    except IOError:
        debug("Error opening file")
        raise SystemExit(74)
    source = file.read()
    debug(source)
    # InterpretResult result = interpret(source);


def example():
    chunk = Chunk()
    constant1 = chunk.add_constant(1.3)
    constant2 = chunk.add_constant(3.1415)
    chunk.write_chunk(OpCode.OP_CONSTANT, 1)
    chunk.write_chunk(constant1, 1)
    chunk.write_chunk(OpCode.OP_CONSTANT, 2)
    chunk.write_chunk(constant2, 2)
    chunk.write_chunk(OpCode.OP_RETURN, 2)
    print chunk

    chunk.disassemble("test chunk")


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()

    if len(argv) > 1:
        runFile(argv[1])
    elif len(argv) == 1:
        pass
        # repl mode baby!
        #repl(stdin)
        example()
    else:
        print "Usage: bt [path]"
        raise SystemExit(64)
    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point, None


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        runFile(filename = sys.argv[1])
    else:
        debug("This will be a repl... eventually")
        #repl()
        example()