'''This is the main program file for the auto grader program.
Auto_grader takes as input:
    --directory (-d) [REQUIRED]: the directory containing all the student directories
where their assignment submissions are located in the appriopriate assignment
sub-directory.
    --assignment (-a) [REQUIRED]: the assignment number that is to be graded
    --student (-s) [OPTIONAL]: the specific student (id) to mark

Auto_grader leverages the following assumptions:
    1) The specified directory containing the students' submissions has the following
    structure:
        ./{studentID}/A{asn_num}/{asn_program}, where:
            studentID takes the form of STUDENT_REG_EX
            asn_num is the assinment number (ex: 1 would be 'A1', 2 is 'A2', etc)
            asn_program is the main program that the student submits and that
                the auto_grader will run to test its correctness
                (ex: warehouse.py)
                NOTE: The directory structure configurations can be changed in ./config.py

    2) The independent program 'student_grader' must be packaged with the desired
        files and configurations to properly run the students' assignment.
            (see student_grader/asn_config.py to modify each assignment's configurations and dependencies)

    3) All exceptions related to assignment grading is handled and caredd for in
        the student_grader program so that if exceptional behavior occurs then
        this program is unaware of it and is returned an appropriate result of the
        grader with a (presumably) grade of 0 and an error message for student
        feedback.
'''
from collections import defaultdict
import csv
import fcntl    # FILe LOCKING
import subprocess
import sys
import os
import re
from optparse import OptionParser
import config
import student_grader.grade as grade
#from student_grader.output.document import Document
#from student_grader.output.output_format import TextFormat
from student_grader.exception.input_exception import InputException
#from student_grader.assignment.assignment import Assignment, AssignmentReport
from student import Student
import traceback

# CONSTANTS
ASSIGNMENT_NUM = 1 # DEFAULT assignment if not specified at command line
CSV_DELIMTER = ","  # Separator for table-like entries in CSV file
STUDENT_REG_EX = re.compile("[a-z]+\d*")    # character(s)-digit(s)

LOG = open("log","w")

def check_input(options):
    '''Validates input arguments'''
    input_errors = []
    if (options.student_directory is None):
        input_errors.append("-d (--directory) was not provided")
    elif (not os.path.isdir(options.student_directory)):
        input_errors.append("The specified student directory is invalid")
    if (options.assignment_num is None):
        #LOG: "No assignment specified, defaulting to assignment #" + str(ASSIGNMENT_NUM)
        options.assignment_num = ASSIGNMENT_NUM

    if (len(input_errors) > 0):
        input_errors.insert(0, "Invalid input arguments:")
        raise InputException('\n\t'.join(input_errors))

def grade_students_assignment(students, assignment_num, process=False):
    '''Runs the student_grader program for each student on the specified assignment number'''
    asn_config = config.assignment(assignment_num)
    for student in students:
        #print(student.directory_path, file=LOG)
        LOG.flush()

        student_grader_args = []

        for module_path in asn_config.relative_paths():
            student_grader_args.append(student.directory_path + '/' + module_path)

        if process:
            print("call:", ["python3", "student_grader/grade.py"] + student_grader_args)
            subprocess.call(["python3", "student_grader/grade.py"] + student_grader_args)
        else:
            student_grader_args = [None] + student_grader_args
            assignment_report = grade.main(student_grader_args)
            student.report(assignment_report)

def generate_student_reports(students, assignment_num):
    '''
    Gerenates the overall reports for all students (CSV file,
    and Assignment and TestCase statistics to STDOUT)
    '''
    assignment_reports = []  # Overall grades for all students
    test_case_reports = defaultdict(list)  # Overall grades per test case
    csv_stats = []  # Rows for a CSV table containgin student's grades per test case
    csv_filename = "A{0}.csv".format(assignment_num)

    asn_config = config.assignment(assignment_num)

    if not os.path.isfile(csv_filename):
        with open(csv_filename, 'a', newline='') as fp:
            # Need to make sure the CSV Header is printed first
            # If auto_grader is run on subsets of students
            fcntl.flock(fp, fcntl.LOCK_EX)

            # Need to create CSV header rows
            test_cases_fn = []
            test_cases = []
            # Find first student with an assignment report to get test Cases
            student_number = 0
            while (students[student_number].get_assignment_report() is None and student_number < len(students)):
                # print(student_number)
                student_number += 1

            if student_number >= len(students):
                raise Exception("Assignment failed to run for all students")

            score = 0
            for tc_result in students[student_number].get_assignment_report().test_case_results:
                test_cases_fn.append(tc_result.test_case.function.__name__)
                test_cases.append(tc_result.test_case)
                #score += tc_result.test_case

            test_cases_fn.sort()
            test_cases_fn.insert(0, 'cdfid')   #cdfid represents studentID column
            test_cases_fn.append("total")    # Total/Assignment grade for student
            csv_stats.append(test_cases_fn)  # Colums are the test cases

            # Input row of MAX grade for each test case
            max_grades = ["max"]
            total_score = 0
            for test_case in test_cases:
                max_grades.append(test_case.max_grade)
                total_score += test_case.max_grade
            max_grades.append(total_score)
            #csv_stats.append(max_grades)

            writer = csv.writer(fp, delimiter=CSV_DELIMTER)
            writer.writerows(csv_stats)
            fcntl.flock(fp, fcntl.LOCK_UN)
        # END writing header to CSV
    # END if CSV file already exists

    csv_stats = []
    for student in students:
        assignment_report = student.get_assignment_report()
        student_test_grades = [student.id]
        student_test_total = 0
        if assignment_report is not None:
            # print(assignment_report.grade)
            assignment_reports.append(assignment_report.grade)

            test_case_results = assignment_report.test_case_results
            # .sort() to ensure test_cases are retrieved in the same order for each student
            test_case_results.sort()
            for test_case_result in test_case_results:
                test_case_reports[test_case_result.test_case].append(test_case_result.grade)
                student_test_grades.append(str(test_case_result.grade))
                student_test_total += test_case_result.grade

            student_test_grades.append(student_test_total)
        csv_stats.append(student_test_grades)

    # Print out test case and assignment stats
    #print('Assignment Statistics:')
    #print_stats(assignment_reports)
    for test_case in test_case_reports.keys():
        print('TestCase ({0}) Statistics:'.format(test_case))
        print_stats(test_case_reports[test_case])

    print("Generating CSV file")
    with open(csv_filename, 'w') as fp:
        writer = csv.writer(fp, delimiter=CSV_DELIMTER)
        fcntl.flock(fp, fcntl.LOCK_EX)
        print(csv_stats)
        writer.writerows(csv_stats)
        fcntl.flock(fp, fcntl.LOCK_UN)

def print_stats(reports):

    if (reports):

        if(isinstance(reports[0],int)):
            print('\tMinimum: {0}'.format(min(reports)))
            print('\tMaximum: {0}'.format(max(reports)))
            print('\tMean: {0}'.format(sum(reports) / len(reports)))
            print('\tMedian: {0}'.format(median(reports)))
        else:
                #remove entries that are an inconsistent length
                if not isinstance(reports[0], float):
                    target = len(reports[0]);

                    for i in range(0,len(reports)):

                        # deslinquent results are all set to 0
                        if (reports[i] == 0):
                            reports[i] = [0]*target
                        elif len(reports[i]) < target:
                            reports[i] = [0]*target

                    for i in range(0,len(reports[0])):
                        sublist = [item[i] for item in reports]
                        print("Subtest {0}:".format(i))
                        print('\tMinimum: {0}'.format(min(sublist)))
                        print('\tMaximum: {0}'.format(max(sublist)))
                        print('\tMean: {0}'.format(sum(sublist) / len(sublist)))
                        print('\tMedian: {0}'.format(median(sublist)))            

def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
        return None
    if len(lst) % 2 == 1:
        return lst[int((len(lst) + 1) / 2) - 1]

    return float((lst[int(len(lst) / 2) - 1] + lst[int(len(lst) / 2)]) / 2.0)

def main(argv):
    try:
        (options, args) = parser.parse_args(argv)
        check_input(options)

        directory_names = [x[1] for x in os.walk(options.student_directory)]
        student_directories = []
        students = []

        # Make sure all students
        if (options.student is None):   # Grade ALL students
            for directories in directory_names:
                for directory_name in directories:
                    if STUDENT_REG_EX.match(directory_name):                                           
                        student_directories.append(directory_name)
                        students.append(Student(directory_name, options.student_directory +
                                                '/' + directory_name))
        else:
            # Grade only the specified student's assignment
            student_directory = options.student_directory + "/" + options.student
            if (os.path.isdir(student_directory)): # Make sure full path to student directory is valid
                student_directories.append(options.student)
                students.append(Student(options.student, student_directory))
            else:
                raise InputException("The supplied student directory and student is not a valid path: "
                                     + student_directory)

        assignment_num = options.assignment_num
        print(students)
        grade_students_assignment(students, assignment_num, options.process)

        if not options.process:
            generate_student_reports(students, assignment_num)

        LOG.close()
        print("Exiting Auto Grader successfully")
    except InputException as ex:
        print(ex)
        LOG.close()
        print("Quitting Auto Grader with traceback: {0}".format(traceback.format_exc()))


parser = OptionParser()
parser.add_option("-d", "--directory",
                  action="store", type="string", dest="student_directory")
parser.add_option("-a", "--assignment",
                  action="store", type="string", dest="assignment_num")
parser.add_option("-s", "--student",
                  action="store", type="string", dest="student")
parser.add_option("-p", "--process",
                  action="store_true", dest="process",
                  help="run the grading as a separate process")
if __name__ == '__main__':
    main(sys.argv)
