from rpython.rlib import rfile
from scanner import Scanner, TokenTypes, TokenTypeToName

LINE_BUFFER_LENGTH = 1024


def repl(stdin, stdout):
    while True:
        stdout.write("> ")
        source = stdin.readline(LINE_BUFFER_LENGTH)

        scanner = Scanner(source)
        t = scanner.scan_token()
        while t.type != TokenTypes.EOF and t.type != TokenTypes.ERROR:
            print TokenTypeToName[t.type],
            if t.type == TokenTypes.NUMBER:
                print "(%s)" % scanner.get_token_string(t),
            print
            t = scanner.scan_token()


def entry_point(argv):
    stdin, stdout, stderr = rfile.create_stdio()
    try:
        repl(stdin, stdout)
    except:
        pass
    return 0


def target(driver, *args):
    driver.exe_name = "scanner2"
    return entry_point, None


if __name__ == '__main__':
    entry_point([])