from chunk import Chunk
from opcodes import OpCode
from vm import VM


def entry_point(argv):
    bytecode = Chunk()
    constant = bytecode.add_constant(1)
    bytecode.write_chunk(OpCode.OP_CONSTANT)
    bytecode.write_chunk(constant)

    constant = bytecode.add_constant(2)
    bytecode.write_chunk(OpCode.OP_CONSTANT)
    bytecode.write_chunk(constant)

    bytecode.write_chunk(OpCode.OP_ADD)
    bytecode.write_chunk(OpCode.OP_RETURN)

    vm = VM()
    vm.interpret_chunk(bytecode)

    return 0


def target(driver, *args):
    driver.exe_name = "vm3"
    return entry_point, None
