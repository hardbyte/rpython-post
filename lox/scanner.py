
_current_id = 0


def _inc_id():
    global _current_id
    _current_id += 1
    return _current_id


class TokenTypes:
    LEFT_PAREN = _inc_id()
    RIGHT_PAREN = _inc_id()
    LEFT_BRACE = _inc_id()
    RIGHT_BRACE = _inc_id()
    COMMA = _inc_id()
    DOT = _inc_id()
    MINUS = _inc_id()
    PLUS = _inc_id()
    SEMICOLON = _inc_id()
    SLASH = _inc_id()
    STAR = _inc_id()

    # One or two character tokens.
    BANG = _inc_id()
    BANG_EQUAL = _inc_id()
    EQUAL = _inc_id()
    EQUAL_EQUAL = _inc_id()
    GREATER = _inc_id()
    GREATER_EQUAL = _inc_id()
    LESS = _inc_id()
    LESS_EQUAL = _inc_id()

    # Literals.
    IDENTIFIER = _inc_id()
    STRING = _inc_id()
    NUMBER = _inc_id()

    # Keywords.
    AND = _inc_id()
    CLASS = _inc_id()
    ELSE = _inc_id()
    FALSE = _inc_id()
    FUN = _inc_id()
    FOR = _inc_id()
    IF = _inc_id()
    NIL = _inc_id()
    OR = _inc_id()
    PRINT = _inc_id()
    RETURN = _inc_id()
    SUPER = _inc_id()
    THIS = _inc_id()
    TRUE = _inc_id()
    VAR = _inc_id()
    WHILE = _inc_id()

    ERROR = _inc_id()
    EOF = _inc_id()


TokenTypeToName = {getattr(TokenTypes, op): op
                        for op in dir(TokenTypes) if not op.startswith('_')}


class BaseToken(object):
    """
    BaseToken's just have a TokenType and source line.
    """

    def __init__(self, line, type):
        self.line = line
        self.type = type


class Token(BaseToken):
    """
    Token's have a line, start, length
    """

    def __init__(self, start, length, line, type):
        super(Token, self).__init__(line, type)
        self.start = start
        self.length = length


class ErrorToken(BaseToken):
    """
    ErrorToken's have an error message.
    """

    def __init__(self, message, line):
        super(ErrorToken, self).__init__(line, TokenTypes.ERROR)
        self.message = message


class Scanner(object):

    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_token(self):
        """Return a token"""
        self._skip_whitespace()
        self.start = self.current

        if self._is_at_end():
            return self._make_token(TokenTypes.EOF)

        char = self.advance()

        if char.isalpha():
            return self._make_identifier()

        if char.isdigit():
            return self._number()

        if char == '(':
            return self._make_token(TokenTypes.LEFT_PAREN)
        if char == ')':
            return self._make_token(TokenTypes.RIGHT_PAREN)
        if char == '{':
            return self._make_token(TokenTypes.LEFT_BRACE)
        if char == '}':
            return self._make_token(TokenTypes.RIGHT_BRACE)
        if char == ';':
            return self._make_token(TokenTypes.SEMICOLON)
        if char == ',':
            return self._make_token(TokenTypes.COMMA)
        if char == '.':
            return self._make_token(TokenTypes.DOT)
        if char == '-':
            return self._make_token(TokenTypes.MINUS)
        if char == '+':
            return self._make_token(TokenTypes.PLUS)
        if char == '/':
            return self._make_token(TokenTypes.SLASH)
        if char == '*':
            return self._make_token(TokenTypes.STAR)

        if char == "!":
            return self._make_token(TokenTypes.BANG_EQUAL if self._match('=') else TokenTypes.BANG)

        if char == "=":
            return self._make_token(TokenTypes.EQUAL_EQUAL if self._match('=') else TokenTypes.EQUAL)

        if char == "<":
            return self._make_token(TokenTypes.LESS_EQUAL if self._match('=') else TokenTypes.LESS)

        if char == ">":
            return self._make_token(TokenTypes.GREATER_EQUAL if self._match('=') else TokenTypes.GREATER)

        if char == '"':
            return self._make_string()

        return self._error_token("Unexpected character")

    def _is_at_end(self):
        return len(self.source) == self.current

    def _make_token(self, token_type):
        return Token(
            start=self.start,
            length=(self.current - self.start),
            line=self.line,
            type=token_type
        )

    def _error_token(self, message):
        return ErrorToken(message, self.line)

    def get_token_string(self, token):
        if isinstance(token, ErrorToken):
            return token.message
        else:
            return self.source[token.start:(token.start+token.length)]

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def _match(self, expected):
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def _skip_whitespace(self):
        while True:
            char = self._peek()

            if char in ' \r\t':
                self.advance()
            elif char == '\n':
                self.line += 1
                self.advance()
            elif char == '/':
                if self._peek_next() == '/':
                    while self._peek() != '\n' and not self._is_at_end():
                        self.advance()
            else:
                return

    def _peek(self):
        if self.current == len(self.source):
            # At the end
            return '\0'
        return self.source[self.current]

    def _peek_next(self):
        if self._is_at_end():
            return '\0'
        return self.source[self.current+1]

    def _make_string(self):
        # We just store the lexeme
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self.advance()

        if self._is_at_end():
            return self._error_token("Unterminated string.")

        # claim the closing "
        self.advance()
        return self._make_token(TokenTypes.STRING)

    def _number(self):
        while self._peek().isdigit():
            self.advance()

        # Look for decimal point
        if self._peek() == '.' and self._peek_next().isdigit():
            self.advance()
            while self._peek().isdigit():
                self.advance()

        return self._make_token(TokenTypes.NUMBER)

    def _make_identifier(self):
        while self._peek().isalpha() or self._peek().isdigit():
            self.advance()
        return self._make_token(self._identifier())

    def _identifier(self):
        char = self.source[self.start]

        if char == 'a':
            return self._check_keyword(1, 2, "nd", TokenTypes.AND)
        if char == 'c':
            return self._check_keyword(1, 4, "lass", TokenTypes.CLASS)
        if char == 'e':
            return self._check_keyword(1, 3, "lse", TokenTypes.ELSE)
        if char == 'f':
            if self.current - self.start > 1:
                char2 = self.source[self.start + 1]
                if char2 == 'a':
                    return self._check_keyword(2, 3, 'lse', TokenTypes.FALSE)
                elif char2 == 'o':
                    return self._check_keyword(2, 1, 'r', TokenTypes.FOR)
                elif char2 == 'u':
                    return self._check_keyword(2, 1, 'n', TokenTypes.FUN)
        if char == 'i':
            return self._check_keyword(1, 1, "f", TokenTypes.IF)
        if char == 'n':
            return self._check_keyword(1, 2, "il", TokenTypes.NIL)
        if char == 'o':
            return self._check_keyword(1, 1, "r", TokenTypes.OR)
        if char == 'p':
            return self._check_keyword(1, 4, "rint", TokenTypes.PRINT)
        if char == 'r':
            return self._check_keyword(1, 5, "eturn", TokenTypes.RETURN)
        if char == 's':
            return self._check_keyword(1, 4, "uper", TokenTypes.SUPER)
        if char == 't':
            if self.current - self.start > 1:
                char2 = self.source[self.start + 1]
                if char2 == 'h':
                    return self._check_keyword(2, 2, 'is', TokenTypes.THIS)
                elif char2 == 'r':
                    return self._check_keyword(2, 2, 'ue', TokenTypes.TRUE)
        if char == 'v':
            return self._check_keyword(1, 2, "ar", TokenTypes.VAR)
        if char == 'w':
            return self._check_keyword(1, 4, "hile", TokenTypes.WHILE)

        return TokenTypes.IDENTIFIER

    def _check_keyword(self, start, length, rest, type):
        if self.source[self.start + start: self.start + start+ length] == rest:
            return type
        else:
            return TokenTypes.IDENTIFIER
