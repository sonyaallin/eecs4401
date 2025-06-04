class OutputFormat:
    '''Abstract/Template class for formatting output to a file/document.
    '''

    def write(self, document, file):
        self.output_header(document, file)
        self.output_body(document, file)
        self.output_footer(document, file)

    def output_header(self, document, file):
        raise NotImplementedError('Need override this implementation')

    def output_body(self, document, file):
        raise NotImplementedError('Need override this implementation')

    def output_footer(self, document, file):
        raise NotImplementedError('Need override this implementation')

class TextFormat(OutputFormat):
    '''Formatting for a txt document.
    '''

    def output_header(self, document, file):
        file.write(document.header)

    def output_body(self, document, file):
        file.write(document.body)

    def output_footer(self, document, file):
        pass
