from lox.debug import disassemble_instruction
from lox.value import Value, ValueArray


class Chunk:
    code = None
    constants = None
    lines = None

    def __init__(self):
        self.code = []
        self.lines = []
        self.constants = ValueArray()

    def write_chunk(self, byte, line):
        self.code.append(byte)
        self.lines.append(line)

    def __repr__(self):
        return "<Chunk of %d bytes>" % (len(self.code))

    def disassemble(self, name):
        print "== %s ==\n" % name
        i = 0
        while i < len(self.code):
            i = disassemble_instruction(self, i)

    def add_constant(self, value):
        if not isinstance(value, Value):
            value = Value(value)
        return self.constants.append(value)
