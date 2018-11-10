from rpython.rlib import rfile
from compiler import Compiler

LINE_BUFFER_LENGTH = 1024


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()

    try:
        while True:
            stdout.write("> ")
            source = stdin.readline(LINE_BUFFER_LENGTH)
            compiler = Compiler(source, debugging=True)
            compiler.compile()
    except:
        pass
    return 0


def target(driver, *args):
    driver.exe_name = "compiler1"
    return entry_point, None


if __name__ == '__main__':
    entry_point([])