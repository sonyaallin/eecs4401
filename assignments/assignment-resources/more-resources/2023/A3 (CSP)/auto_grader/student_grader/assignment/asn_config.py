class AssignmentConfig:
    '''Configurations to make the assignment executable.
        dependencies - Assignment dependent Modules/Files which should be bundled within the python package
    '''
    DEPENDENCY_FOLDER = 'dependencies'

    def __init__(self, dependencies):
        self._dependencies = dependencies   # Libraries

    @property
    def dependencies(self):
        return self._dependencies

def assignment(num):
    '''Helper method to access AssignmentConfigs'''
    return assignments[str(num)]

assignments = {
    '1': AssignmentConfig(
            [   # Assignment dependent Modules/Files
                # These should be bundled with the python package
                "search.py",
                "sokoban.py"                
            ]
        ),
    '2': AssignmentConfig(
            [   # Assignment dependent Modules/Files
                # These should be bundled with the python package
                "cspbase.py"            
            ]
        ),
    '3': AssignmentConfig(
            [   # Assignment dependent Modules/Files
                # These should be bundled with the python package
                "cspbase.py"            
            ]
        ),    
    '4': AssignmentConfig(
            [   # Assignment dependent Modules/Files
                # These should be bundled with the python package
                "BayesianNetwork.py",
                "MedicalBayesianNetwork.py"
            ]
        ),
    }
