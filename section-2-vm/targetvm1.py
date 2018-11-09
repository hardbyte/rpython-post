from chunk import Chunk
from opcodes import OpCode


def entry_point(argv):
    # create a chunk
    bytecode = Chunk()
    bytecode.write_chunk(OpCode.OP_ADD)
    bytecode.write_chunk(OpCode.OP_RETURN)

    bytecode.disassemble("adding example")

    return 0

# _____ Define and setup target ___


def target(driver, *args):
    driver.exe_name = "vm1"
    return entry_point, None

