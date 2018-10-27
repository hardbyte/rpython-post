from lox.opcodes import OpCode

OpCodeToInstructionName = {getattr(OpCode, op): op
                           for op in dir(OpCode) if op.startswith('OP_')}


def leftpad_string(string, width, char=" "):
    l = len(string)
    if l > width:
        return string
    return char * (width - l) + string


def rightpad_string(string, width, char=" "):
    l = len(string)
    if l > width:
        return string
    return string + char * (width - l)


def simple_instruction(name, offset):
    print ""
    return offset + 1


def constant_instruction(name, chunk, offset):
    constant = chunk.code[offset + 1]
    print "(%s)" % leftpad_string("%d" % constant, 2, '0'),
    print "%s" % leftpad_string("'%s'" % chunk.constants[constant].debug_repr(), 8)
    return offset + 2


def disassemble_instruction(chunk, offset):
    print leftpad_string("%d" % offset, 4, '0'),

    instruction = chunk.code[offset]
    if instruction not in OpCodeToInstructionName:
        print "Unknown opcode %s" % instruction
        return offset + 1

    # Print the line number
    if offset > 0 and chunk.lines[offset] == chunk.lines[offset - 1]:
        print "   | ",
    else:
        print leftpad_string(str(chunk.lines[offset]), 4),

    # Print the opcode's name
    instruction_name = OpCodeToInstructionName[instruction]
    print rightpad_string("%s " % instruction_name, 12),


    # Now the opcode specific output
    if instruction == OpCode.OP_CONSTANT:
        return constant_instruction(instruction_name, chunk, offset)

    return simple_instruction(instruction_name, offset)


