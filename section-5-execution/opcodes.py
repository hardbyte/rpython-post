
class OpCode:
    """
    The OpCodes of our language's VM
    """

    OP_CONSTANT = 0
    OP_RETURN = 1
    OP_NEGATE = 2
    OP_ADD = 3
    OP_SUBTRACT = 4
    OP_MULTIPLY = 5
    OP_DIVIDE = 6

    BinaryOps = {
        OP_ADD: "+",
        OP_SUBTRACT: "-",
        OP_MULTIPLY: "*",
        OP_DIVIDE: "/"
    }