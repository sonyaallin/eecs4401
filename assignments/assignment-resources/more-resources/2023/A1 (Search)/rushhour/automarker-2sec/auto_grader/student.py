class Student:
    '''Represents a student and the information pertaining to
    grading their assignment. Specifically their directory path
    in order to access their individual and unique assignments
    '''

    def __init__(self, id, directory_path):
        '''Construct a new Student'''
        self.id = id
        self.directory_path = directory_path
        self.assignment_reports = dict()

    def run_assignment(self, assignment, test_case):
        student_result = assignment.run(self.directory_path, test_case)
        return student_result

    def report(self, assignment_report):
        '''Report the result of the test case on the specified assignment'''
        self.assignment_report = assignment_report

    def get_assignment_report(self):
        '''Return AssignmentReport for the specified Assignment'''
        return self.assignment_report
