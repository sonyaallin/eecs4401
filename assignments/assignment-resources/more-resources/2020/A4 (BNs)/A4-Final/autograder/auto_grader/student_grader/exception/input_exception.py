class InputException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{0.__class__.__name__}: {0.message}".format(self)
