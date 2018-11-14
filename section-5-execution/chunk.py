from debug import disassemble_instruction


class Chunk:
    code = None
    constants = None

    def __init__(self):
        self.code = []
        self.constants = []
        self._constants = {}

    def write_chunk(self, byte):
        self.code.append(byte)

    def disassemble(self, name):
        print "== %s ==\n" % name
        i = 0
        while i < len(self.code):
            i = disassemble_instruction(self, i)

    def add_constant(self, value):
        # See if we already know this constant
        if value in self._constants:
            return self._constants[value]
        else:
            index = len(self._constants)
            self.constants.append(value)
            self._constants[value] = index
            return index
