from lox.scanner import Scanner, TokenTypes, TokenTypeToName


def compile(source):
    scanner = Scanner(source)

    line = -1
    while True:
        token = scanner.scan_token()
        if token.line != line:
            print "Line ", token.line
            line = token.line
        else:
            print "   | "

        print TokenTypeToName[token.type], scanner.get_token_string(token)

        if token.type == TokenTypes.EOF:
            break
