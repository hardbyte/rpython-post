from lox.opcodes import OpCode

OpCodeToInstructionName = {getattr(OpCode, op): op for op in dir(OpCode) if op.startswith('OP_')}

def simple_instruction(name, offset):
    print name


def disassemble_instruction(instruction, offset):
    print "{:04d}".format(offset),

    if instruction not in OpCodeToInstructionName:
        print "Unknown opcode %s" % instruction
        return

    return simple_instruction(OpCodeToInstructionName[instruction], offset)

