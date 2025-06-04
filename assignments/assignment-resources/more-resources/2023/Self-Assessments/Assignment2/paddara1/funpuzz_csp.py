#Look for #IMPLEMENT tags in this file.
'''
Construct and return funpuzz CSP models.
'''
import itertools
from cspbase import *


def binary_ne_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only binary all-different
    constraints for both the row and column constraints.

    Returns a CSP object representing a FunPuzz Grid CSP problem along with an array of variables
    for the problem. That is return:

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using binary constraints
    to enforce row and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """
    # each constraint has two variables
    csp = CSP("binary_ne_grid")
    size = funpuzz_grid[0][0]  # grid is size x size
    all_combs = list(itertools.combinations(range(size), 2))  # list of all constraints
    sat_tuples = list(itertools.permutations(range(1, size + 1), 2))  # list of all satisfying tuples
    domain = [i + 1 for i in range(size)]
    vars_ = [[None for _ in range(size)] for _ in range(size)]  # 2d array to store variables
    for item in funpuzz_grid[1:]:
        if len(item) == 2:
            # cell item[0] must have the value item[1]
            row = int(str(item[0])[0]) - 1
            col = int(str(item[0])[1]) - 1
            var = Variable(str(row) + str(col), [item[1]])
            vars_[row][col] = var
            csp.add_var(var)

    for row in range(size):
        for col in range(size):
            if vars_[row][col] is None:  # don't add same variable twice
                var = Variable(f"V{row}{col}", domain)
                csp.add_var(var)
                vars_[row][col] = var

    for i in range(size):
        column = []
        for j in range(size):
            column.append(vars_[j][i])
        for row, col in all_combs:
            con1 = Constraint(f"C{row}{col}", [vars_[i][row], vars_[i][col]])
            con2 = Constraint(f"C{row}{col}", [column[row], column[col]])
            con1.add_satisfying_tuples(sat_tuples)
            con2.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(con1)
            csp.add_constraint(con2)

    return csp, vars_


def nary_ad_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only n-ary all-different
    constraints for both the row and column constraints.

    Returns a CSP object representing a Cageoky Grid CSP problem along with an array of variables
    for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using n-ary constraints to enforce row
    and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """
    csp = CSP("nary_ad_grid")
    size = funpuzz_grid[0][0]  # grid is size x size
    domain = [i + 1 for i in range(size)]
    sat_tuples = list(itertools.permutations(range(1, size + 1), size))  # list of all satisfying tuples
    vars_ = [[None for _ in range(size)] for _ in range(size)]  # 2d array to store variables
    for item in funpuzz_grid[1:]:
        if len(item) == 2:
            # cell item[0] must have the value item[1]
            row = int(str(item[0])[0]) - 1
            col = int(str(item[0])[1]) - 1
            var = Variable(str(row) + str(col), [item[1]])
            vars_[row][col] = var
            csp.add_var(var)

    for row in range(size):
        for col in range(size):
            if vars_[row][col] is None:  # don't add same variable twice
                var = Variable(f"V{row}{col}", domain)
                csp.add_var(var)
                vars_[row][col] = var

    for i in range(size):
        column = []
        for j in range(size):
            column.append(vars_[j][i])
        con1 = Constraint(f"CRow{i}", vars_[i])
        con2 = Constraint(f"CCol{i}", column)
        con1.add_satisfying_tuples(sat_tuples)
        con2.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(con1)
        csp.add_constraint(con2)
    return csp, vars_


def funpuzz_csp_model(funpuzz_grid):
    """A model built using your choice of (1) binary binary not-equal, or (2) n-ary all-different
    constraints for the grid, together with (3) funpuzz cage constraints. That is, you will
    choose one of the previous two grid models and expand it to include cage constraints
    for the funpuzz Variation.

    Returns a CSP object representing a Cageoky Grid CSP problem along with an array of variables
    for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using constraints
    to enforce cage, row and column constraints and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does require implementation of cage constraints.
    """
    csp, vars_ = binary_ne_grid(funpuzz_grid)
    for cage in funpuzz_grid[1:]:
        if len(cage) == 2:
            # cell cage[0] must have the value cage[1]
            row = int(str(cage[0])[0]) - 1
            col = int(str(cage[0])[1]) - 1
            con = Constraint(f"C{row}{col}", [vars_[row][col]])
            con.add_satisfying_tuples([(cage[1], )])
        elif len(cage) > 2:
            op = cage[-1]  # operation
            target = cage[-2]
            cells = cage[:-2]  # List of cells in this cage
            cage_domains = []  # List[List] containing domain of each var in this cage
            cage_vars = []  # List[Variable]
            for cell in cells:
                row = int(str(cell)[0]) - 1
                col = int(str(cell)[1]) - 1
                cage_domains.append(vars_[row][col].domain())
                cage_vars.append(vars_[row][col])

            domain_all_combs = list(itertools.product(*cage_domains))  # cartesian product of all domains
            sat_tuples = get_sat_tuples(op, target, domain_all_combs)
            con = Constraint(f"Cage{target} {op}", cage_vars)
            con.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(con)

    return csp, vars_


def get_sat_tuples(operation: int, target: int, domains):
    """
    Helper function for funpuzz_csp_model.
    Return a list of satisfying tuples for this cage.
    :param operation: 0 or 1 or 2 or 3
    :param target:
    :param domains:
    :return: list of satisfying tuples for this cage.
    """
    ans = []
    if operation == 0:  # add
        for dom in domains:
            curr_sum = 0
            for value in dom:
                curr_sum += value
            if curr_sum == target:
                ans.append(dom)

    elif operation == 1:  # subtract
        for dom in domains:
            all_perms = list(itertools.permutations(dom))
            for perm in all_perms:
                diff = subtract_list(perm)
                if diff == target:
                    ans.append(dom)

    elif operation == 2:  # divide
        for dom in domains:
            all_perms = list(itertools.permutations(dom))
            for perm in all_perms:
                quotient = divide_list(perm)
                if quotient == target:
                    ans.append(dom)

    elif operation == 3:  # multiply
        for dom in domains:
            curr_product = 1
            for value in dom:
                curr_product *= value
            if curr_product == target:
                ans.append(dom)
    return ans


def subtract_list(lst) -> int:
    """
    Let n = len(lst)
    Return lst[0] - lst[1] - ... - lst[n-1]
    :param lst: List[int]
    """
    if not lst:
        return 0
    elif len(lst) == 1:
        return lst[0]
    else:
        return lst[0] - (sum(lst[1:]))


def divide_list(lst) -> int:
    """
    Let n = len(lst)
    Return lst[0] / lst[1] / ... / lst[n-1]
    :param lst: List[int]
    """
    if not lst:
        return 0
    elif len(lst) == 1:
        return lst[0]
    else:
        ans = lst[0]
        for num in lst[1:]:
            ans /= num
        return ans
