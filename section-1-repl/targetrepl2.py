from rpython.rlib import rfile

LINE_BUFFER_LENGTH = 1024


def repl(stdin):
    while True:
        print "> ",
        line = stdin.readline(LINE_BUFFER_LENGTH)
        print line


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()
    try:
        repl(stdin)
    except:
        return 0


def target(driver, *args):
    return entry_point, None
