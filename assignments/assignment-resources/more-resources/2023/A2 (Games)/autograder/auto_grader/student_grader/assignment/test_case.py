import gc

from utils.utilities import setMEM, resetMEM

class TestCaseResult:
    '''Represents....
    This class should be considered immutable as it is just a wrapper class to
    encapsulate the information stored for a test case run.
    '''

    def __init__(self, test_case, grade, details):
        '''Constructs a new TestCaseResult'''
        self._test_case = test_case # Function name
        self._details = details

        if grade is not True and grade is not False:
            self._grade = grade
        elif grade:
            self._grade = test_case.max_grade
        else:
            self._grade = 0
            

    def __lt__(self, other):
        '''Delegates comparison to test case object.
        '''
        return self.test_case < other.test_case

    @property
    def test_case(self):
        return self._test_case

    @property
    def grade(self):
        return self._grade

    @property # Delegate Method
    def max_grade(self):
        return self.test_case.max_grade

    @property
    def details(self):
        return self._details

    def __str__(self):
        return "TestCase: {0.test_case}\t{0.grade}/{0.max_grade}\n{0.details}".format(self)

import sys
class TestCase:
    '''Represents a Test-Case with the specified function encapsulating the
    test-case logic.
    '''
    def __init__(self, function, max_grade):
        self._function = function
        self._max_grade = max_grade

    def __lt__(self, other):
        '''Compare function names as strings to determine ordering
        '''
        return self.function.__name__ < other.function.__name__

    def execute(self, assignment_module):
        '''Run the TestCase on the specified assignment module
        Returns the TestCaseResult obect from invoking this TestCase's _function
        '''
        print("running test_case ", self)
        sys.stdout.flush()
        setMEM(4096)
        try:
            value = self._function(assignment_module)
        except MemoryError:
            gc.collect()
            value = 0, "MemoryError occurred"
        resetMEM()
        gc.collect()
        return value

    @property
    def function(self):
        return self._function

    @property
    def max_grade(self):
        return self._max_grade

    def __str__(self):
        return "[function={0.function.__name__}]" \
                .format(self)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
                self.function == other.function and \
                self.max_grade == other.max_grade

    def __hash__(self):
        return self.function.__hash__() + self.max_grade
