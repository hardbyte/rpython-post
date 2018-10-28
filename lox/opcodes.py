

class OpCode:
    """
    The OpCodes of our language's VM
    """

    OP_CONSTANT = 0
    OP_RETURN = 1
    OP_TEST = 2
    OP_NEGATE = 3
    OP_ADD = 4
    OP_SUBTRACT = 5
    OP_MULTIPLY = 6
    OP_DIVIDE = 7

    BinaryOps = {
        OP_ADD: "+",
        OP_SUBTRACT: "-",
        OP_MULTIPLY: "*",
        OP_DIVIDE: "/"
    }