
from scanner import Scanner, TokenTypes, TokenTypeToName


def entry_point(argv):

    source = "(  1  + 2.0 )"

    scanner = Scanner(source)
    t = scanner.scan_token()
    while t.type != TokenTypes.EOF and t.type != TokenTypes.ERROR:
        print TokenTypeToName[t.type],
        if t.type == TokenTypes.NUMBER:
            print "(%s)" % scanner.get_token_string(t),
        print
        t = scanner.scan_token()
    return 0


def target(driver, *args):
    driver.exe_name = "scanner1"
    return entry_point, None


if __name__ == '__main__':
    entry_point([])