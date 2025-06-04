class Document:
    '''Group the components of a document together.
    '''

    def __init__(self, header, body):
        self._header = header
        self._body = body

    def save(self, filepath, format):
        with open(filepath, "w") as file:
	        format.write(self, file)

    @property
    def header(self):
        return self._header

    @property
    def body(self):
        return self._body
