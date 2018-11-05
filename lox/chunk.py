from lox.debug import disassemble_instruction
from lox.value import Value, ValueArray


class Linesman(object):
    """
    A run-length encoding object tracking the source code
    line numbers for all chunk's instructions.
    """
    def __init__(self):
        self.rle = []

    def append(self, line):
        if len(self.rle) == 0 or self.rle[-1][0] != line:
            self.rle.append([line, 1])
        else:
            # incr line count
            self.rle[-1][1] += 1

    def _index_rle(self, rle, item):
        rle_count = 0
        for line_number, repeats in rle:
            rle_count += repeats
            if rle_count > item:
                return line_number
        return -1

    def __getitem__(self, item):
        return self._index_rle(self.rle, item)


class Chunk:
    code = None
    constants = None
    lines = None

    def __init__(self):
        self.code = []
        self.lines = Linesman()
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
