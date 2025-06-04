#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools

def bi_helper(variable_array, domain, mode=0):
    cons = []
    for r, row in enumerate(variable_array):
        for i in range(0, len(variable_array)):
            for j in range(i+1, len(variable_array)):
                tmp_scope = (variable_array[row][i], variable_array[row][j])
                if mode == 0:
                    name = "C" + str(r) + str(i) + ":" + str(r) + str(j)
                else:
                    name = "C" + str(i) + str(r) + ":" + str(j) + str(r)
                tmp_cons = Constraint(name, tmp_scope)
                sat_tuples = [k for k in itertools.permutations(domain, 2)]
                tmp_cons.add_satisfying_tuples(sat_tuples)
                cons.append(tmp_cons)
    return cons
                
def n_helper(variable_array, domain, mode=0):
    cons = []
    for r, row in enumerate(variable_array):
        tmp_scope = row
        if mode == 0:
            name = "C_row" + str(r)
        else:
            name = "C_col" + str(r)
        tmp_cons = Constraint(name, tmp_scope)
        sat_tuples = [k for k in itertools.permutations(domain, len(variable_array))]
        tmp_cons.add_satisfying_tuples(sat_tuples)
        cons.append(tmp_cons)
    return cons
        


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
    dim = funpuzz_grid[0][0]
    domain = range(1, dim+1)
    variables, variable_array = [], []
    for i in domain:
        row = []
        for j in domain:
            name = str(i) + str(j)
            var = Variable(name, domain)
            row.append(var)
            variables.append(var)
        variable_array.append(row)
    # constraints
    row_cons = bi_helper(variable_array, domain)
    col_cons = bi_helper([list(i) for i in zip(*variable_array)], domain, 1)
    cons = row_cons + col_cons
    csp_model = CSP("binary_constraints_model", variables)
    for i in cons:
        csp_model.add_constraint(i)
    return csp_model, variable_array


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
    dim = funpuzz_grid[0][0]
    domain = range(1, dim + 1)
    variables, variable_array = [], []
    for i in domain:
        row = []
        for j in domain:
            name = str(i) + str(j)
            var = Variable(name, domain)
            row.append(var)
            variables.append(var)
        variable_array.append(row)
    # constraints
    row_cons = n_helper(variable_array, domain)
    col_cons = n_helper([list(i) for i in zip(*variable_array)], domain, 1)
    cons = row_cons + col_cons
    csp_model = CSP("n-ary_constraints_model", variables)
    for i in cons:
        csp_model.add_constraint(i)
    return csp_model, variable_array


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
    csp, variable_array = nary_ad_grid(funpuzz_grid)
    constraints = funpuzz_grid[1:]
    for num, c in enumerate(constraints):
        if len(c) == 2:
            i, j = c[0] // 10, c[0] % 10
            tmp_scope = [variable_array[i-1][j-1]]
            name = "C_cage:" + str(num)
            tmp_cons = Constraint(name, tmp_scope)
            sat_tuples = [c[1]]
            tmp_cons.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(tmp_cons)
        else:
            target = c[-2]
            operation = c[-1]
            tmp_vars = c[:-2]
            tmp_scope = []
            for i in tmp_vars:
                x, y = i // 10, i % 10
                tmp_scope.append(variable_array[x-1][y-1])
            name = "C_cage:" + str(num)
            tmp_cons = Constraint(name, tmp_scope)
            sat_tuples = []
            for i in itertools.product(range(1, len(variable_array)+1), repeat=len(tmp_scope)):
                tmp_result = i[0]
                for j in i[1:]:
                    if operation == 0:
                        tmp_result += j
                    elif operation == 1:
                        tmp_result -= j
                    elif operation == 2:
                        tmp_result /= j
                    elif operation == 3:
                        tmp_result *= j
                    else:
                        raise Exception("invalid operation")
                if tmp_result == target:
                    sat_tuples.append(i)
            tmp_tuples = []
            for i in sat_tuples:
                for j in itertools.permutations(i, len(i)):
                    if j not in sat_tuples:
                        tmp_tuples.append(j)
            tmp_cons.add_satisfying_tuples(sat_tuples)

            if len(tmp_tuples) != 0:
                tmp_cons.add_satisfying_tuples(tmp_tuples)
            csp.add_constraint(tmp_cons)

    return csp, variable_array


