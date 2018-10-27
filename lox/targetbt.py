"""


"""
from lox import Chunk, OpCode
from rpython.rlib import rfile


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

    file = rfile.create_file(filename, 'r')
    source = file.read()
    debug(source)

    # filepoint = os.open(filename, os.O_RDWR, 0777)
    # while True:
    #     payload = os.read(filepoint, 1024)
    #     if len(payload) == 0:
    #         break
    #     debug(payload)
    # os.close(filepoint)


def example():
    chunk = Chunk()
    chunk.write_chunk(OpCode.OP_RETURN)
    chunk.write_chunk(OpCode.OP_RETURN)
    print chunk

    chunk.disassemble("test chunk")


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()

    if len(argv) > 1:
        runFile(argv[1])
    elif len(argv) == 1:
        # repl mode baby!
        #repl(stdin)
        example()
    else:
        print "Usage: bt [path]"

    return 0

# _____ Define and setup target ___

def target(*args):
    return entry_point, None


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        runFile(filename = sys.argv[1])
