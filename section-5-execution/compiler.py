# coding=utf-8
from chunk import Chunk
from opcodes import OpCode
from scanner import Scanner, TokenTypes


class Parser(object):
    def __init__(self):
        self.had_error = False
        self.panic_mode = False
        self.current = None
        self.previous = None


class Precedence(object):
    NONE = 0
    DEFAULT = 1
    TERM = 6        # + -
    FACTOR = 7      # * /
    UNARY = 8       # ! - +
    CALL = 9        # ()
    PRIMARY = 10


class ParseRule(object):
    def __init__(self, prefix, infix, precedence):
        self.prefix = prefix
        self.infix = infix
        self.precedence = precedence


class Compiler(object):

    def __init__(self, source, debugging=True):
        self.parser = Parser()
        self.scanner = Scanner(source)
        # The chunk of bytecode we are currently assembling
        self.chunk = Chunk()
        self.DEBUG_PRINT_CODE = debugging

    def compile(self):
        self.advance()
        self.expression()
        self.consume(TokenTypes.EOF, "Expect end of expression.")
        self.end_compiler()

        return not self.parser.had_error

    def _error_at(self, token, msg):
        if self.parser.panic_mode:
            # suppress subsequent errors
            return
        print "[error detected at character %d]" % token.start

        if token.type == TokenTypes.EOF:
            print " at end"
        elif token.type == TokenTypes.ERROR:
            pass
        else:
            print " at %s" % self.scanner.get_token_string(token)
        print ": %s\n" % msg

        self.parser.had_error = True

    def error_at_current(self, msg):
        self._error_at(self.parser.current, msg)

    def error(self, msg):
        self._error_at(self.parser.previous, msg)

    def end_compiler(self):
        self._emit_return()

        if self.DEBUG_PRINT_CODE and not self.parser.had_error:
            self.chunk.disassemble("code")

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
        constant = self.chunk.add_constant(value)
        if constant > 255:
            self.error("Too many constants in one chunk.")
            return 0
        return constant

    def emit_byte(self, byte):
        self.chunk.write_chunk(byte)

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
        prefix_rule = self._get_rule(self.parser.previous.type).prefix
        if prefix_rule is None:
            self.error("Expected expression.")
            return
        else:
            prefix_rule(self)

        while precedence <= self._get_rule(self.parser.current.type).precedence:
            self.advance()
            infix_method = self._get_rule(self.parser.previous.type).infix
            infix_method(self)

    def number(self):
        value = float(self.scanner.get_token_string(self.parser.previous))
        self._emit_constant(value)

    def expression(self):
        self.parse_precedence(Precedence.DEFAULT)

    @staticmethod
    def _get_rule(op_type):
        return rules[op_type]


# The table that drives our whole parser. Entries per token of:
# [ prefix, infix, precedence]
rules = [
    ParseRule(None,                 None,               Precedence.NONE),        # ERROR
    ParseRule(None,                 None,               Precedence.NONE),        # EOF
    ParseRule(Compiler.grouping,    None,               Precedence.CALL),        # LEFT_PAREN
    ParseRule(None,                 None,               Precedence.NONE),        # RIGHT_PAREN
    ParseRule(Compiler.unary,       Compiler.binary,    Precedence.TERM),        # MINUS
    ParseRule(None,                 Compiler.binary,    Precedence.TERM),        # PLUS
    ParseRule(None,                 Compiler.binary,    Precedence.FACTOR),      # SLASH
    ParseRule(None,                 Compiler.binary,    Precedence.FACTOR),      # STAR
    ParseRule(Compiler.number,      None,               Precedence.NONE),        # NUMBER
]
