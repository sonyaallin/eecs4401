from functools import wraps

def max_grade(max_grade_value):
    '''Adds the 'max_grade' annotation'''
    def max_grade_decorator(func):
        '''Adds the 'max_grade' attribute to the specified function'''
        func.max_grade = max_grade_value
        @wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper
    return max_grade_decorator
