

class Value(object):
    """
    Boxing of values.

    """
    def __init__(self, value):
        self.value = value

    def debug_repr(self):
        if isinstance(self.value, float):
            return ("%f" % self.value)[:6]
        else:
            return str(self.value)



class ValueArray(object):
    def __init__(self):
        self.values = []

    def __getitem__(self, item):
        return self.values[item]

    def append(self, value):
        """

        :param value:
        :return: The index of the added constant/value
        """
        self.values.append(value)
        return len(self.values) - 1

