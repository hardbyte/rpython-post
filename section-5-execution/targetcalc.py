from rpython.rlib import rfile
from compiler import Compiler
from vm import VM

LINE_BUFFER_LENGTH = 2**20


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()
    vm = VM()

    while True:
        stdout.write("> ")
        source = stdin.readline(LINE_BUFFER_LENGTH).strip()
        if not source:
            break
        compiler = Compiler(source, debugging=True)

        if compiler.compile():
            vm.interpret_chunk(compiler.chunk)

    return 0


def target(driver, *args):
    driver.exe_name = "calc"
    return entry_point, None


if __name__ == '__main__':
    entry_point([])