#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import *

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
    # board size nxn
    n = funpuzz_grid[0][0]
    variables = []
    var_array = []
    # creating satisfying tuples, the second argument is 2 because we just want binary permutations
    p = permutations(list(range(1, n + 1)), 2)
    tuples = []
    for perm in p:
        tuples.append(perm)
    # creating scopes for constraints, number of constraints = 2 * n
    constraints = []
    constraints_num = len(list(combinations(list(range(1, n + 1)), 2))) * n * n
    for i in range(constraints_num):
        c_name = str(i)
        c = Constraint(c_name, [])
        constraints.append(c)

    # creating variables
    for i in range(n):
        var_array.append([])
        for j in range(n):
            var_name = "{}{}".format(i, j)
            var_domain = list(range(1, n + 1))
            var = Variable(var_name, var_domain)
            var_array[i].append(var)
            variables.append(var)

    # note that every constraint has 2 variables, so I need to add the
    # possible binary combinations of the variables in the row and column
    # to a given constraint
    constraint_index = 0

    # adding row combinations to constraints
    # looping through all rows
    for row_i in range(n):
        # getting the possible binary combination of variables per row
        var_comb = list(combinations(var_array[row_i], 2))
        # looping and adding variable combination to a constraint scope
        for comb in var_comb:
            constraints[constraint_index].scope.extend(list(comb))
            constraint_index += 1

    # adding column combinations to constraints
    for column_i in range(n):
        column = []
        for row_i in range(n):
            column.append(var_array[row_i][column_i])
        # getting the possible binary combination of variables per row
        var_comb = list(combinations(column, 2))
        # looping and adding variable combination to a constraint scope
        for comb in var_comb:
            constraints[constraint_index].scope.extend(list(comb))
            constraint_index += 1

    # adding satisfying tuples to constraints
    for c in constraints:
        c.add_satisfying_tuples(tuples)

    # creating CSP
    csp = CSP("binary", variables)
    for c in constraints:
        csp.add_constraint(c)

    return csp, var_array


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
    n = funpuzz_grid[0][0]
    variables = []
    var_array = []
    # creating satisfying tuples
    p = permutations(list(range(1, n + 1)), n)
    tuples = []
    for perm in p:
        tuples.append(perm)
    # creating scopes for constraints, number of constraints = 2 * n
    constraints = []
    for i in range(n * 2):
        c_name = str(i)
        c = Constraint(c_name, [])
        constraints.append(c)

    # creating variables
    for i in range(n):
        var_array.append([])
        for j in range(n):
            var_name = "{}{}".format(i, j)
            var_domain = list(range(1, n + 1))
            var = Variable(var_name, var_domain)
            var_array[i].append(var)
            variables.append(var)
            constraints[j].scope.append(var)
            constraints[i + n].scope.append(var)

    # adding satisfying tuples to constraints
    for c in constraints:
        c.add_satisfying_tuples(tuples)

    csp = CSP("n-ary", variables)
    for c in constraints:
        csp.add_constraint(c)

    return csp, var_array


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
    csp, var_array = nary_ad_grid(funpuzz_grid)
    # operation (0=’+’, 1=’-’, 2=’/’, 3=’*’)
    #  [[3], [11,12,13,6,0], [21,22,31,2,2], ....]
    num = 0
    for cage in funpuzz_grid[1:]:
        operation = cage[-1]
        result = cage[-2]
        cells = cage[:-2]
        scope = []
        for cell in cells:
            row = int(str(cell)[0]) - 1
            column = int(str(cell)[1]) - 1
            var = var_array[row][column]
            scope.append(var)
        name = "Cage{}: {}".format(num, operation)
        constraint = Constraint(name, scope)
        num += 1
        # creating the satisfying tuples
        tuples = satisfy(scope, result, operation)
        constraint.add_satisfying_tuples(tuples)
        csp.add_constraint(constraint)
    return csp, var_array

# ------------------------- start helper functions -------------------------
def satisfy(variables, result, operation):
    domain = variables[0].domain()
    possible_combinations = list(product(domain, repeat=len(variables)))
    tuples = []
    for comb in possible_combinations:
        temp_result = comb[0]
        for value in comb[1:]:
            if operation == 0:
                temp_result += value
            elif operation == 1:
                temp_result = abs(temp_result - value)
            elif operation == 2:
                temp_result /= value
            else:
                temp_result *= value
        if temp_result == result:
            if operation == 2:
                comb_list = (list(permutations(comb, len(comb))))
                for tup in comb_list:
                    tuples.append(tup)
            else:
                tuples.append(comb)
    return tuples

# -------------------------- end helper functions --------------------------
