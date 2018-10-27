from lox.debug import disassemble_instruction


class Chunk:
    code = None

    def __init__(self):
        self.code = bytearray(0)

    def write_chunk(self, byte):
        self.code.append(byte)

    def __repr__(self):
        return "<Chunk of {} bytes>".format(len(self.code))

    def disassemble(self, name):
        print "== %s ==\n" % name
        for i, instruction in enumerate(self.code):
            disassemble_instruction(instruction, i)

