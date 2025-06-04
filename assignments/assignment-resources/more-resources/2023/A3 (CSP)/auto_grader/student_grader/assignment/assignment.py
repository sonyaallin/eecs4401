import os
import imp
import importlib
from .test_case import TestCaseResult

from sys import argv

class Assignment:
    """Represents an arbitrary assignment
    which encapsulates the information needed to run the assignment
    """
    def __init__(self, num, module_paths, test_cases):
        """Constructs a new Assignment"""
        self.num = num
        print(module_paths)
        self.module_paths = module_paths
        self.test_cases = test_cases
        self.test_cases.sort()
        self.NULL_REPORT = AssignmentReport(self)
        for test_case in test_cases:
            test_case_result = TestCaseResult(test_case, 0, "Could not run Assignment.")
            self.NULL_REPORT.report_test_case(test_case_result)

    def run(self, test_case):

        #print("running {}".test_case)
        
        """Runs the assignment and returns the result.
        Throws an 'Exception' if the assignment could not be run or times out
        """
        path_modules = {}   # Dictionary containing assignment's modules
        for module_path in self.module_paths:
            # Keys are the module's filename (including extension) EX: search.py
            module_file = os.path.basename(module_path)
            try:
                # -- This(importlib command) caused bug in code to load previous student's module for first test
                # When run using auto_grader
                #self.solution_module = importlib.import_module(self.program_path)
                module = imp.load_source(module_path, module_path)
                path_modules[module_file] = module
            except ImportError as ex:
                #raise ImportError("Unable to import student file at {0}".format(module_path))
                # Let students submit part of assignment
                print("Unable to import student file at {0}".format(module_path))
                print(ex)
                path_modules[module_file] = None
            except FileNotFoundError as ex:
                print("Student file at {0} does not exist.".format(module_path))
                path_modules[module_file] = None

                print(path_modules)

        grade, details = test_case.execute(path_modules)    # Run test case and return TestCaseResult
        return TestCaseResult(test_case, grade, details)

class AssignmentReport:

    def __init__(self, assignment):
        '''Constructs a new AssignmentReport'''
        self._assignment = assignment
        self._test_case_results = []
        self._grade = 0
        self._max_grade = 0

    def report_test_case(self, results):
        '''Adds a test case result to the specified test case'''
        self._test_case_results.append(results)        
        #self._grade += results.grade
        self._max_grade += results.max_grade

    def dump(self):
        print([t.grade for t in self.test_case_results])

    @property
    def assignment(self):
        return self._assignment

    @property
    def test_case_results(self):
        return self._test_case_results

    @property
    def grade(self):
        return self._grade

    @property
    def max_grade(self):
        return self._max_grade
