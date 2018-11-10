from opcodes import OpCode
from debug import disassemble_instruction, get_printable_location


class IntepretResultCode:
    INTERPRET_OK = 0
    INTERPRET_COMPILE_ERROR = 1
    INTERPRET_RUNTIME_ERROR = 2


IntepretResultToName = {getattr(IntepretResultCode, op): op
                        for op in dir(IntepretResultCode) if op.startswith('INTERPRET_')}


class VM(object):
    STACK_MAX_SIZE = 256

    chunk = None
    stack = None
    stack_top = 0

    # Instruction Pointer (or Program Counter)
    # points to the next instruction to be executed
    ip = 0

    def __init__(self, debug=True):
        self.debug_trace = debug
        self._reset_stack()

    def _reset_stack(self):
        self.stack = [0] * self.STACK_MAX_SIZE
        self.stack_top = 0

    def _stack_push(self, value):
        assert self.stack_top < self.STACK_MAX_SIZE
        self.stack[self.stack_top] = value
        self.stack_top += 1

    def _stack_pop(self):
        assert self.stack_top >= 0
        self.stack_top -= 1
        return self.stack[self.stack_top]

    def _print_stack(self):
        print "         ",
        if self.stack_top <= 0:
            print "[]",
        else:
            for i in range(self.stack_top):
                print "[ %s ]" % self.stack[i],
        print

    def _run(self):
        while True:
            if self.debug_trace:
                self._print_stack()
                disassemble_instruction(self.chunk, self.ip)
            instruction = self._read_byte()

            if instruction == OpCode.OP_RETURN:
                print "%s" % self._stack_pop()
                return IntepretResultCode.INTERPRET_OK
            elif instruction == OpCode.OP_CONSTANT:
                constant = self._read_constant()
                self._stack_push(constant)
            elif instruction == OpCode.OP_NEGATE:
                operand = self._stack_pop()
                operand *= -1
                self._stack_push(operand)
            elif instruction == OpCode.OP_ADD:
                self._binary_op(self._stack_add)
            elif instruction == OpCode.OP_SUBTRACT:
                self._binary_op(self._stack_subtract)
            elif instruction == OpCode.OP_MULTIPLY:
                self._binary_op(self._stack_multiply)
            elif instruction == OpCode.OP_DIVIDE:
                self._binary_op(self._stack_divide)


    @staticmethod
    def _stack_add(op1, op2):
        return op1 + op2

    @staticmethod
    def _stack_subtract(op1, op2):
        return op1 - op2

    @staticmethod
    def _stack_multiply(op1, op2):
        return op1 * op2

    @staticmethod
    def _stack_divide(op1, op2):
        return op1 / op2

    def interpret_chunk(self, chunk):
        if self.debug_trace:
            print "== VM TRACE =="
        self.chunk = chunk
        self.ip = 0
        try:
            result = self._run()
            return result
        except:
            return IntepretResultCode.INTERPRET_RUNTIME_ERROR

    def _read_byte(self):
        instruction = self.chunk.code[self.ip]
        self.ip += 1
        return instruction

    def _read_constant(self):
        constant_index = self._read_byte()
        return self.chunk.constants[constant_index]

    def _binary_op(self, operator):
        op2 = self._stack_pop()
        op1 = self._stack_pop()
        result = operator(op1, op2)
        self._stack_push(result)
