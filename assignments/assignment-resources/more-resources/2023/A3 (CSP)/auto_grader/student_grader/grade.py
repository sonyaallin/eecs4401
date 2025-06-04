import importlib
import inspect
import random
import shutil   # For copying dependent files to sandbox
import string
import subprocess
import sys
import traceback
import os
import re
import assignment.asn_config as asn_config
from assignment.assignment import Assignment, AssignmentReport
from output.document import Document
from exception.input_exception import InputException
from output.output_format import TextFormat
from assignment.test_case import TestCase, TestCaseResult

# CONSTANTS
DEFAULT_ASSIGNMENT_NUM = 3 # Assignment wanting to grade (default if not specified)
FILENAME_RESULTS = "_results.txt"
MSG_EARLY_TERMINATION = "An Error (most likely from the instructors) caused the grader to terminate prematurely.\n"
FILENAME_TEST_CASES = "A2_test_cases.py"
DEPENDENCY_FOLDER = "dependencies"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, CURRENT_DIR + '/' + DEPENDENCY_FOLDER)

import assignment.A2_test_cases as test_cases_module

def create_sandbox_environment(assignment_directory, sandbox_directory, dependencies):
    os.mkdir(sandbox_directory)
    sys.path.insert(0, assignment_directory)    # Make sure student code can be imported
    sys.path.insert(0, sandbox_directory)    # Make sure dependecies use supplied code

    for dependency in dependencies:
        shutil.copy(CURRENT_DIR + '/' + DEPENDENCY_FOLDER + '/' + dependency, sandbox_directory + '/' + dependency)

def delete_sandbox_environment(assignment_directory, sandbox_directory):
    if os.path.isdir(sandbox_directory):
        shutil.rmtree(sandbox_directory)
    if sandbox_directory in sys.path:
        sys.path.remove(sandbox_directory)
    if assignment_directory in sys.path:
        sys.path.remove(assignment_directory)

def grade_assignment(assignment):
    assignment_report = AssignmentReport(assignment)
    for test_case in assignment.test_cases:

        print(test_case)
        try:
            test_case_result = assignment.run(test_case)
            sys.stdout.flush()
        except Exception as ex:
            # traceback.print_exc()
            test_case_result = TestCaseResult(test_case, 0,
                                               "{exception} was raised: {message}\n{traceback}".format(
                                                exception=type(ex).__name__, message=str(ex), traceback=traceback.format_exc()
                                                ))

        assignment_report.report_test_case(test_case_result)

    return assignment_report

def generate_report(assignment_report, directory):
    test_case_reports = dict()  # Overall grades per test case

    student_report_body = ['Overall: ' + str(assignment_report.grade) + '/' + str(assignment_report.max_grade)]
    for test_case_result in assignment_report.test_case_results:
        test_case = test_case_result.test_case
        test_case_reports[test_case] = test_case_result
        student_report_body.append('Test Case: ' + str(test_case) + '\t['
                                   + str(test_case_result.grade) + '/' + str(test_case_result.max_grade)
                                   + ']\n\t' + str(test_case_result.details))

    document = Document(header(assignment_report.assignment.num), ('\n' + ('=' * 20) + '\n').join(student_report_body))
    document.save(directory + '/' + FILENAME_RESULTS, TextFormat())

    # Print out assignment stats
    print("\n====")
    print("Assignment Grade: {0}/{1}".format(assignment_report.grade, assignment_report.max_grade))

    # Print out test case stats
    print('\nTestCase Statistics:')
    for test_case, test_case_result in test_case_reports.items():
        print("\t{0}: ".format(str(test_case)), "{grade}/{max_grade}".format(grade=test_case_result.grade, max_grade=test_case_result.max_grade))

def header(assignment_num):
    return \
    ('#' * 20) + '\n' + \
    '# ' + 'Assignment ' + str(assignment_num) + '\n' + \
    ('#' * 20) + '\n\n'

def check_input(argv):
    if len(argv) < 2:
        raise InputException("Expected parameter 'assignment_program(s)' is missing")
    else:
        for i in range(1, len(argv)):
            if not os.path.isfile(argv[i]):
                #raise InputException("The specified assignment filepath '{0}' is invalid".format(argv[i]))
                print("The specified assignment filepath '{0}' is invalid".format(argv[i]))


def main(argv):
    '''Grades the assignment specified at the input argument.
    '''

    assignment_report = None
    assignment_directory = sandbox_directory = ""
    # Check test cases are present
    test_case_tuples = inspect.getmembers(test_cases_module, inspect.isfunction)

    test_cases = []
    for test_case_tuple in test_case_tuples:
        test_case_function = test_case_tuple[1]
        if inspect.getmodule(test_case_function) == test_cases_module:
            # Make sure functions do not include ones imported within test cases file
            test_cases.append(TestCase(test_case_function, test_case_function.max_grade))

    assignment = None


    try:
        NULL_REPORT = AssignmentReport(None)
        for test_case in test_cases:
            print(test_case)
            test_case_result = TestCaseResult(test_case, 0, "Could not run Assignment.")
            NULL_REPORT.report_test_case(test_case_result)
        assignment_report = NULL_REPORT

        check_input(argv)   # Check user input

        if len(test_cases) == 0:
            raise InputException("No test cases were found in {0}".format(FILENAME_TEST_CASES))

        assignment_paths = argv[1:] # Retrieve all student modules
        ASSIGNMENT_NUM = DEFAULT_ASSIGNMENT_NUM
        assignment = Assignment(ASSIGNMENT_NUM, assignment_paths, test_cases)

        assignment_directory = os.path.dirname(os.path.realpath(assignment_paths[0]))

        sandbox_directory = assignment_directory + '/.tmp'
        while os.path.exists(sandbox_directory):    # Make sure to get a unique sandbox directory
            sandbox_directory += random.choice(string.ascii_letters)

        assignment_dependecies = asn_config.assignment(ASSIGNMENT_NUM).dependencies
        create_sandbox_environment(assignment_directory, sandbox_directory, assignment_dependecies)
        print("START Grading Assignment ", str(assignment_paths))
        assignment_report = grade_assignment(assignment)
        print("Done Grading Assignment ", str(assignment_paths))
        generate_report(assignment_report, assignment_directory)
        print('DONE generating assignment report ', str(assignment_paths))
    except InputException as ex:
        print(MSG_EARLY_TERMINATION)
        print(traceback.format_exc())
    except IOError as ex:
        print(MSG_EARLY_TERMINATION)
        print(traceback.format_exc())
    except ImportError as ex:
        print(MSG_EARLY_TERMINATION)
        print(traceback.format_exc())
    except AttributeError as ex:
        print(MSG_EARLY_TERMINATION)
        print(traceback.format_exc())
    finally:
        pass
        #delete_sandbox_environment(assignment_directory, sandbox_directory)

    if __name__ == "__main__":
        assignment_report.dump()
        with open("output.csv","a") as output_file:
            output_line = ",".join([str(t.grade) for t in assignment_report.test_case_results])
            output_file.write(output_line+"\n")
        return

    return assignment_report

if __name__ == '__main__':
    main(sys.argv)
