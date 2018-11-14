from debug import disassemble_instruction


class Chunk:
    code = None
    constants = None

    def __init__(self):
        self.code = []
        self.constants = []

    def write_chunk(self, byte):
        self.code.append(byte)

    def disassemble(self, name):
        print "== %s ==\n" % name
        i = 0
        while i < len(self.code):
            i = disassemble_instruction(self, i)

    def add_constant(self, value):
        self.constants.append(value)
        return len(self.constants) - 1
