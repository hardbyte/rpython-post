# coding=utf-8
from lox.scanner import Scanner, TokenTypes, TokenTypeToName


class Parser(object):
    def __init__(self):
        self.had_error = False
        self.panic_mode = False
        self.current = None
        self.previous = None


class Compiler(object):
    """
    A single pass compiler using Pratt’s parsing technique.
    Note it might be interesting to create a version that
    parses to an AST, then a code generator traverses the AST
    and outputs bytecode.
    """

    def __init__(self, source):
        self.parser = Parser()
        self.scanner = Scanner(source)

    def compile(self):

        # todo could be scanner.advance
        self.advance()
        self.expression()

        self.consume(TokenTypes.EOF, "Expect end of expression.")

        return not self.parser.had_error

    def _error_at(self, token, msg):
        if self.parser.panic_mode:
            # suppress subsequent errors
            return
        print "[line %d] Error" % token.line

        if token.type == TokenTypes.EOF:
            print " at end"
        elif token.type == TokenTypes.ERROR:
            pass
        else:
            print " at %s" % self.scanner.source[token.start:token.start+token.length]
        print ": %s\n" % msg

        self.parser.had_error = True

    def error_at_current(self, msg):
        self._error_at(self.parser.current, msg)

    def error(self, msg):
        self._error_at(self.parser.previous, msg)

    def advance(self):
        self.parser.previous = self.parser.current

        while True:
            self.parser.current = self.scanner.scan_token()
            if self.parser.current.type != TokenTypes.ERROR:
                break
            self.error_at_current(self.parser.current.message)

    def consume(self, token_type, msg):
        if self.parser.current.type == token_type:
            self.advance()
            return

        self.error_at_current(msg)


