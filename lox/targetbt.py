"""


"""
from lox import Chunk, OpCode, VM
from lox.errors import LoxCompileError, LoxRuntimeError
from lox.vm import IntepretResultToName, IntepretResultCode
from rpython.rlib import rfile
import os


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


def debug(msg):
    print "debug:", msg


def repl(stream):
    vm = VM()
    while True:
        print "> ",
        next_line = stream.readline()
        if not next_line:
            break
        print "^" + next_line

        vm.interpret(next_line)


def runFile(filename):
    debug("runFile called with: " + filename)

    source = read_file(filename)
    vm = VM(debug=False)
    try:
        result = vm.interpret(source)
        if result == IntepretResultCode.INTERPRET_COMPILE_ERROR:
            print "Compile error"
        elif result == IntepretResultCode.INTERPRET_RUNTIME_ERROR:
            print "Runtime error"
    except ValueError as e:
        print "Unhandled exception in runFile"



def read_file(filename):
    try:
        file = rfile.create_file(filename, 'r')
    except IOError:
        debug("Error opening file")
        raise SystemExit(74)
    source = file.read()
    return source


def example():
    vm = VM()

    chunk = Chunk()
    constant1 = chunk.add_constant(100)
    constant2 = chunk.add_constant(3.1415)
    constant3 = chunk.add_constant(2)

    chunk.write_chunk(OpCode.OP_CONSTANT, 1)
    chunk.write_chunk(constant1, 1)
    chunk.write_chunk(OpCode.OP_NEGATE, 1)
    chunk.write_chunk(OpCode.OP_CONSTANT, 1)
    chunk.write_chunk(constant2, 1)
    chunk.write_chunk(OpCode.OP_DIVIDE, 2)
    chunk.write_chunk(OpCode.OP_CONSTANT, 2)
    chunk.write_chunk(constant3, 2)
    chunk.write_chunk(OpCode.OP_SUBTRACT, 2)
    chunk.write_chunk(OpCode.OP_CONSTANT, 2)
    chunk.write_chunk(constant3, 2)
    chunk.write_chunk(OpCode.OP_MULTIPLY, 2)
    chunk.write_chunk(OpCode.OP_RETURN, 3)
    print chunk

    chunk.disassemble("test chunk")

    print "== Executing in vm =="
    interpreter_result = vm.interpret_chunk(chunk)
    print IntepretResultToName[interpreter_result]


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
        repl(sys.stdin)
        #example()