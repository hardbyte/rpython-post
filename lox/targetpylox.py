"""


"""
from lox import VM
from lox.vm import IntepretResultToName, IntepretResultCode
try:
    from rpython.jit.codewriter.policy import JitPolicy
    from rpython.rlib import rfile
except ImportError:
    # Hopefully running under python
    pass


def jitpolicy(driver):
    return JitPolicy()


DEBUGGING_MESSAGES = False


def debug(msg):
    if DEBUGGING_MESSAGES:
        print "debug:", msg


def repl(stdin, stdout):
    vm = VM()
    print "Welcome to pylox"
    print "https://github.com/hardbyte/pylox"

    while True:
        stdout.write("> ")
        LINE_BUFFER_LENGTH = 1024
        next_line = stdin.readline(LINE_BUFFER_LENGTH)
        if not next_line:
            break
        print

        vm.interpret(next_line)


def runFile(filename):
    debug("runFile called with: " + filename)

    source = read_file(filename)
    vm = VM(debug=False)
    try:
        result = vm.interpret(source)
        debug(IntepretResultToName[result])
        if result == IntepretResultCode.INTERPRET_COMPILE_ERROR:
            print "Compile error"
        elif result == IntepretResultCode.INTERPRET_RUNTIME_ERROR:
            print "Runtime error"
    except ValueError:
        print "Unhandled exception in runFile"


def read_file(filename):
    try:
        file = rfile.create_file(filename, 'r')
    except IOError:
        debug("Error opening file")
        raise SystemExit(74)
    source = file.read()
    return source


def entry_point(argv):
    if len(argv) > 1:
        runFile(argv[1])
    elif len(argv) == 1:
        debug("Entering lox repl")
        stdin, stdout, stderr = rfile.create_stdio()
        repl(stdin, stdout)
    else:
        print "Usage: bt [path]"
        raise SystemExit(64)
    return 0

# _____ Define and setup target ___


def target(driver, *args):
    driver.exe_name = "lox-c"
    return entry_point, None


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2:
        runFile(filename=sys.argv[1])
    else:
        print "Welcome to pylox"
        print "https://github.com/hardbyte/pylox"
        repl(sys.stdin, sys.stdout)
