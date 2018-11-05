# coding=utf-8
from lox import Chunk, OpCode
from lox.scanner import Scanner, TokenTypes, TokenTypeToName


class Parser(object):
    def __init__(self):
        self.had_error = False
        self.panic_mode = False
        self.current = None
        self.previous = None


class Precedence(object):
    NONE = 0
    ASSIGNMENT = 1  # =
    OR = 2          # or
    AND = 3         # and
    EQUALITY = 4    # == !=
    COMPARISON = 5  # < > <= >=
    TERM = 6        # + -
    FACTOR = 7      # * /
    UNARY = 8       # ! - +
    CALL = 9        # . () []
    PRIMARY = 10


class ParseRule(object):
    def __init__(self, prefix, infix, precedence):
        self.prefix = prefix
        self.infix = infix
        self.precedence = precedence

    def __getitem__(self, item):
        if item == 0:
            return self.prefix
        elif item == 1:
            return self.infix
        elif item == 2:
            return self.precedence
        else:
            raise KeyError


# The table that drives our whole parser. Entries per token of:
# [ prefix, infix, precedence]
rules = [
    ParseRule('grouping',    None,       Precedence.CALL),        # TOKEN_LEFT_PAREN
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_RIGHT_PAREN
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_LEFT_BRACE
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_RIGHT_BRACE
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_COMMA
    ParseRule(None,          None,       Precedence.CALL),        # TOKEN_DOT
    ParseRule('unary',       'binary',   Precedence.TERM),        # TOKEN_MINUS
    ParseRule(None,          'binary',   Precedence.TERM),        # TOKEN_PLUS
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_SEMICOLON
    ParseRule(None,          'binary',   Precedence.FACTOR),      # TOKEN_SLASH
    ParseRule(None,          'binary',   Precedence.FACTOR),      # TOKEN_STAR
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_BANG
    ParseRule(None,          None,       Precedence.EQUALITY),    # TOKEN_BANG_EQUAL
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_EQUAL
    ParseRule(None,          None,       Precedence.EQUALITY),    # TOKEN_EQUAL_EQUAL
    ParseRule(None,          None,       Precedence.COMPARISON),  # TOKEN_GREATER
    ParseRule(None,          None,       Precedence.COMPARISON),  # TOKEN_GREATER_EQUAL
    ParseRule(None,          None,       Precedence.COMPARISON),  # TOKEN_LESS
    ParseRule(None,          None,       Precedence.COMPARISON),  # TOKEN_LESS_EQUAL
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_IDENTIFIER
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_STRING
    ParseRule('number',      None,       Precedence.NONE),        # TOKEN_NUMBER
    ParseRule(None,          None,       Precedence.AND),         # TOKEN_AND
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_CLASS
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_ELSE
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_FALSE
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_FUN
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_FOR
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_IF
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_NIL
    ParseRule(None,          None,       Precedence.OR),          # TOKEN_OR
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_PRINT
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_RETURN
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_SUPER
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_THIS
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_TRUE
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_VAR
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_WHILE
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_ERROR
    ParseRule(None,          None,       Precedence.NONE),        # TOKEN_EOF

]


class Compiler(object):
    """
    A single pass compiler using Pratt’s parsing technique.
    Note it might be interesting to create a version that
    parses to an AST, then a code generator traverses the AST
    and outputs bytecode.
    """

    def __init__(self, source, debugging=True):
        self.parser = Parser()
        self.scanner = Scanner(source)
        # The chunk of bytecode we are currently assembling
        self.chunk = Chunk()
        self.DEBUG_PRINT_CODE = debugging

    def compile(self):

        # todo could be scanner.advance
        self.advance()
        self.expression()

        self.consume(TokenTypes.EOF, "Expect end of expression.")
        self.end_compiler()

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

    def end_compiler(self):
        self._emit_return()

        if self.DEBUG_PRINT_CODE and not self.parser.had_error:
            self.current_chunk().disassemble("code")

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

    def make_constant(self, value):
        chunk = self.current_chunk()
        constant = chunk.add_constant(value)
        if constant > 255:
            self.error("Too many constants in one chunk.")
            return 0
        return constant

    def current_chunk(self):
        return self.chunk

    def emit_byte(self, byte):
        self.current_chunk().write_chunk(byte, self.parser.previous.line)

    def emit_bytes(self, byte_a, byte_b):
        self.emit_byte(byte_a)
        self.emit_byte(byte_b)

    def _emit_constant(self, value):
        self.emit_bytes(OpCode.OP_CONSTANT, self.make_constant(value))

    def _emit_return(self):
        self.emit_byte(OpCode.OP_RETURN)

    def grouping(self):
        self.expression()
        self.consume(TokenTypes.RIGHT_PAREN, "Expected ')' after expression.")

    def unary(self):
        op_type = self.parser.previous.type
        # Compile the operand
        self.parse_precedence(Precedence.UNARY)
        # Emit the operator instruction
        if op_type == TokenTypes.MINUS:
            self.emit_byte(OpCode.OP_NEGATE)

    def binary(self):
        op_type = self.parser.previous.type

        # As binary ops are "infix" we've already
        # consumed the left operand.

        # Compile the right operand
        rule = self._get_rule(op_type)
        self.parse_precedence(rule.precedence + 1)

        # Emit the operator instruction
        if op_type == TokenTypes.PLUS: self.emit_byte(OpCode.OP_ADD)
        if op_type == TokenTypes.MINUS: self.emit_byte(OpCode.OP_SUBTRACT)
        if op_type == TokenTypes.STAR: self.emit_byte(OpCode.OP_MULTIPLY)
        if op_type == TokenTypes.SLASH: self.emit_byte(OpCode.OP_DIVIDE)

    def parse_precedence(self, precedence):
        # parses any expression of a given precedence level or higher
        self.advance()
        prefix_rule = self._get_rule(self.parser.previous.type)[0]
        if prefix_rule is None:
            self.error("Expected expression.")
            return
        else:
            prefix_method = getattr(self, prefix_rule)
            prefix_method()

        while precedence <= self._get_rule(self.parser.current.type)[2]:
            self.advance()
            infix_method_name = self._get_rule(self.parser.previous.type)[1]
            infix_method = getattr(self, infix_method_name)
            infix_method()


    def number(self):
        value = float(self.scanner.get_token_string(self.parser.previous))
        self._emit_constant(value)

    def expression(self):
        self.parse_precedence(Precedence.ASSIGNMENT)

    @staticmethod
    def _get_rule(op_type):
        return rules[op_type]


