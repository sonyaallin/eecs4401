'''
Represents the configuration parameters across different assignments.
'''
class Config:

    def __init__(self, directory, modules):
        self._directory = directory
        self._modules = modules

    @property
    def directory(self):
        return self._directory

    @property
    def modules(self):
        return self._modules

    def relative_paths(self):
        module_paths = []
        for module in self.modules:
            module_paths.append(self.directory + '/' + module)
        print("returning", module_paths)
        return module_paths

def assignment(num):
    '''Helper method to access AssignmentConfigs'''
    return assignments[str(num)]


assignments = {
    '1': Config(
            'A1',           # ASN_DIRECTORY
            [
                'solution.py' # ASN_PROGRAM
            ]
        ),
    '2': Config(
            'A2',       # ASN_DIRECTORY
            [   # ASN MODULES (student solutions)
                'kenken_csp.py',
                'orderings.py',
            ]
        ),
    '3': Config(
            'A3',       # ASN_DIRECTORY
            [   # ASN MODULES (student solutions)
                'agent.py'           
            ]
        ),
    '4': Config(
            'A4',       # ASN_DIRECTORY
            [   # ASN MODULES (student solutions)
                'bnetbase.py'           
            ]
        )
    }
