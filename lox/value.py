

class Value(object):
    """
    Boxing of values.

    """
    def __init__(self, value):
        self.value = value

    def debug_repr(self):
        if isinstance(self.value, float):
            return ("%f" % self.value)[:16]
        else:
            return str(self.value)

    def __repr__(self):
        return "<Value: '%s'>" % self.value

    def __eq__(self, other):
        return self.value == other.value


class ValueArray(object):
    def __init__(self):
        self.values = []

    def __getitem__(self, item):
        return self.values[item]

    def index(self, item):
        # Return the index of an item in the array
        for i, value in enumerate(self.values):
            if item.value == value.value:
                return i
        raise ValueError("Not found")

    def append(self, value):
        """

        :param value:
        :return: The index of the added constant/value
        """
        self.values.append(value)
        return len(self.values) - 1

