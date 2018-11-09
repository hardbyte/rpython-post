from rpython.rlib import rfile

LINE_BUFFER_LENGTH = 1024


def repl(stdin, stdout):
    while True:
        stdout.write("> ")
        line = stdin.readline(LINE_BUFFER_LENGTH)
        print '"%s"' % line.strip()


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()
    try:
        repl(stdin, stdout)
    except:
        pass
    return 0


def target(driver, *args):
    return entry_point, None
