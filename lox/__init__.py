from lox.chunk import Chunk
from lox.opcodes import OpCode


if __name__ == "__main__":
    chunk = Chunk()
    chunk.write_chunk(OpCode.OP_RETURN)
    chunk.write_chunk(OpCode.OP_RETURN)
    print chunk

    chunk.disassemble("test chunk")

