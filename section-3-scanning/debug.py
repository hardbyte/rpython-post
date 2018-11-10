from opcodes import OpCode

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
    return "", offset + 1


def binary_instruction(name, chunk, offset):
    return "", offset + 1


def format_constant(name, chunk, constant):
    debug_repr = ("%f" % chunk.constants[constant])[:16]
    return "(%s) %s" % (
        leftpad_string("%d" % constant, 2, '0'),
        leftpad_string("'%s'" % debug_repr, 10)
    )


def constant_instruction(name, chunk, offset):
    constant = chunk.code[offset + 1]
    return format_constant(name, chunk, constant), offset + 2


def get_printable_location(ip, passed_instruction, chunk, vm):
    instruction_index = format_ip(ip)
    instruction = chunk.code[ip]
    instruction_name = format_instruction(get_instruction_name(instruction))
    _, instruction_extras = format_instruction_extended(chunk, instruction, instruction_name, ip)
    return "%s %s %s" % (instruction_index, instruction_name, instruction_extras)


def disassemble_instruction(chunk, offset):
    print format_ip(offset),

    instruction = chunk.code[offset]
    if instruction not in OpCodeToInstructionName:
        print "Unknown opcode %s" % instruction
        return offset + 1

    # Print the opcode's name
    instruction_name = get_instruction_name(instruction)
    print format_instruction(instruction_name),

    # Now the opcode specific output
    ip, repr = format_instruction_extended(chunk, instruction, instruction_name, offset)
    print repr
    return ip


def format_instruction_extended(chunk, instruction, instruction_name, offset):
    # Enrich the representation for constants, binary ops etc

    if instruction == OpCode.OP_CONSTANT:
        assert len(chunk.constants) > 0
        repr, ip = constant_instruction(instruction_name, chunk, offset)
    elif instruction in OpCode.BinaryOps:
        repr, ip = binary_instruction(instruction_name, chunk, offset)
    else:
        repr, ip = simple_instruction(instruction_name, offset)
    return ip, repr


def format_ip(ip):
    return leftpad_string("%d" % ip, 4, '0')


def get_instruction_name(instruction):
    return OpCodeToInstructionName[instruction]


def format_instruction(instruction_name):
    return rightpad_string("%s " % instruction_name, 12)

