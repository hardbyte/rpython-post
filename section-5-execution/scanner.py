

class TokenTypes:
    ERROR = 0
    EOF = 1
    LEFT_PAREN = 2
    RIGHT_PAREN = 3
    MINUS = 4
    PLUS = 5
    SLASH = 6
    STAR = 7
    NUMBER = 8


TokenTypeToName = {getattr(TokenTypes, op): op
                   for op in dir(TokenTypes) if not op.startswith('_')}


class BaseToken(object):
    pass


class Token(BaseToken):

    def __init__(self, start, length, token_type):
        self.type = token_type
        self.start = start
        self.length = length


class ErrorToken(BaseToken):
    """
    ErrorToken's have an error message.
    """

    def __init__(self, message, location):
        self.type = TokenTypes.ERROR
        self.message = message
        self.location = location


class Scanner(object):

    def __init__(self, source):
        self.source = source
        self.start = 0
        self.current = 0

    def scan_token(self):
        """Return a token"""
        self._skip_whitespace()
        self.start = self.current

        if self._is_at_end():
            return self._make_token(TokenTypes.EOF)

        char = self.advance()

        if char.isdigit():
            return self._number()

        if char == '(':
            return self._make_token(TokenTypes.LEFT_PAREN)
        if char == ')':
            return self._make_token(TokenTypes.RIGHT_PAREN)
        if char == '-':
            return self._make_token(TokenTypes.MINUS)
        if char == '+':
            return self._make_token(TokenTypes.PLUS)
        if char == '/':
            return self._make_token(TokenTypes.SLASH)
        if char == '*':
            return self._make_token(TokenTypes.STAR)

        return ErrorToken("Unexpected character", self.current)

    def _is_at_end(self):
        return len(self.source) == self.current

    def _make_token(self, token_type):
        return Token(
            start=self.start,
            length=(self.current - self.start),
            token_type=token_type
        )

    def get_token_string(self, token):
        if isinstance(token, ErrorToken):
            return token.message
        else:
            end_loc = token.start + token.length
            assert end_loc < len(self.source)
            assert end_loc > 0
            return self.source[token.start:end_loc]

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
            if char in ' \r\t\n':
                self.advance()
            elif char == '/':
                if self._peek_next() == '/':
                    while self._peek() != '\n' and not self._is_at_end():
                        self.advance()
                else:
                    break
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

    def _number(self):
        while self._peek().isdigit():
            self.advance()

        # Look for decimal point
        if self._peek() == '.' and self._peek_next().isdigit():
            self.advance()
            while self._peek().isdigit():
                self.advance()

        return self._make_token(TokenTypes.NUMBER)
