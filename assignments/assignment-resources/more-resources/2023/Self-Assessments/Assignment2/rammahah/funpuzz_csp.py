# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations


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
    dimensions = funpuzz_grid[0][0]
    domain = list(range(1, dimensions + 1))
    variable_array = [[0] * dimensions for i in range(dimensions)]
    funpuzz_csp = CSP("Funpuzz Grid")
    for i in range(1, len(funpuzz_grid)):
        cage = funpuzz_grid[i]
        end = len(cage) - 2
        for j in range(end):
            cell = cage[j]
            name = str(cell)
            x = (cell // 10) - 1
            y = (cell % 10) - 1
            new_var = Variable(name, domain)
            variable_array[x][y] = new_var
            funpuzz_csp.add_var(new_var)

    tuples = []
    for i in range(dimensions):
        for j in range(dimensions):
            if i != j:
                tuples.append((i + 1, j + 1))

    for row in variable_array:
        for i in range(dimensions):
            for j in range(i + 1, dimensions):
                var1 = row[i]
                var2 = row[j]
                name = str(var1) + "!=" + str(var2)
                new_con = Constraint(name, [var1, var2])
                new_con.add_satisfying_tuples(tuples)
                funpuzz_csp.add_constraint(new_con)

    for col in range(dimensions):
        for i in range(dimensions):
            for j in range(i + 1, dimensions):
                var1 = variable_array[i][col]
                var2 = variable_array[j][col]
                name = str(var1) + "!=" + str(var2)
                new_con = Constraint(name, [var1, var2])
                new_con.add_satisfying_tuples(tuples)
                funpuzz_csp.add_constraint(new_con)

    return funpuzz_csp, variable_array


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
    dimensions = funpuzz_grid[0][0]
    domain = list(range(1, dimensions + 1))
    variable_array = [[0] * dimensions for i in range(dimensions)]
    funpuzz_csp = CSP("Funpuzz Grid")
    for i in range(1, len(funpuzz_grid)):
        cage = funpuzz_grid[i]
        end = len(cage) - 2
        for j in range(end):
            cell = cage[j]
            name = str(cell)
            x = (cell // 10) - 1
            y = (cell % 10) - 1
            new_var = Variable(name, domain)
            variable_array[x][y] = new_var
            funpuzz_csp.add_var(new_var)

    tuples = list(permutations(domain))

    for row in range(dimensions):
        name = "Row " + str(row + 1) + " All-Diff"
        new_con = Constraint(name, variable_array[row])
        new_con.add_satisfying_tuples(tuples)
        funpuzz_csp.add_constraint(new_con)

    for col in range(dimensions):
        name = "Col " + str(col + 1) + " All-Diff"
        col_list = []
        for i in range(dimensions):
            col_list.append(variable_array[i][col])
        new_con = Constraint(name, col_list)
        new_con.add_satisfying_tuples(tuples)
        funpuzz_csp.add_constraint(new_con)

    return funpuzz_csp, variable_array


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
    dimensions = funpuzz_grid[0][0]
    domain = list(range(1, dimensions + 1))
    variable_array = [[0] * dimensions for i in range(dimensions)]
    funpuzz_csp = CSP("Funpuzz Grid")
    for i in range(1, len(funpuzz_grid)):
        cage = funpuzz_grid[i]
        end = len(cage) - 2
        cage_vars = []
        for j in range(end):
            cell = cage[j]
            name = str(cell)
            x = (cell // 10) - 1
            y = (cell % 10) - 1
            new_var = Variable(name, domain)
            variable_array[x][y] = new_var
            cage_vars.append(new_var)
            funpuzz_csp.add_var(new_var)

        operation = cage[-1]
        result = cage[-2]
        count = len(cage) - 2
        if operation == 0:
            cage_tuples = get_possible_vals_sum(result, dimensions, count)
        elif operation == 1:
            cage_tuples = get_possible_vals_diff(result, dimensions, count)
        elif operation == 2:
            cage_tuples = get_possible_vals_quot(result, dimensions, count)
        elif operation == 3:
            cage_tuples = get_possible_vals_product(result, dimensions, count)
        else:  # operation value is invalid
            cage_tuples = []
        name = "Cage " + str(i)
        new_con = Constraint(name, cage_vars)
        new_con.add_satisfying_tuples(cage_tuples)
        funpuzz_csp.add_constraint(new_con)

    tuples = list(permutations(domain))

    for row in range(dimensions):
        name = "Row " + str(row + 1) + " All-Diff"
        new_con = Constraint(name, variable_array[row])
        new_con.add_satisfying_tuples(tuples)
        funpuzz_csp.add_constraint(new_con)

    for col in range(dimensions):
        name = "Col " + str(col + 1) + " All-Diff"
        col_list = []
        for i in range(dimensions):
            col_list.append(variable_array[i][col])
        new_con = Constraint(name, col_list)
        new_con.add_satisfying_tuples(tuples)
        funpuzz_csp.add_constraint(new_con)

    return funpuzz_csp, variable_array


def get_possible_vals_sum(result, max_val, count):
    if result < 1:
        return [[-1]]
    if count == 1:
        if max_val >= result:
            return [[result]]
        else:
            return [[-1]]
    possibilities = []
    for i in range(1, max_val + 1):
        if i <= result - count + 1:
            sub_possibilities = get_possible_vals_sum(result - i, max_val,
                                                      count - 1)
            for p in sub_possibilities:
                if p[0] != -1:
                    new = [i] + p
                    possibilities.append(new)

    if not possibilities:
        return [[-1]]
    return possibilities


def get_possible_vals_diff(result, max_val, count):
    if result < 1:
        return [[-1]]
    if count == 1:
        if max_val >= result:
            return [[result]]
        else:
            return [[-1]]
    possibilities = []
    for i in range(1, max_val + 1):
        if i - result >= count - 1:
            sub_possibilities = get_possible_vals_sum(i - result, max_val,
                                                      count - 1)
            for p in sub_possibilities:
                if p[0] != -1:
                    new = [i] + p
                    possibilities.append(new)

    if not possibilities:
        return [[-1]]
    tuples = []
    for x in possibilities:
        tuples += permutations(x)
    return list(set(tuples))


def get_possible_vals_product(result, max_val, count):
    if result < 1:
        return [[-1]]
    if count == 1:
        if max_val >= result:
            return [[result]]
        else:
            return [[-1]]
    possibilities = []
    for i in range(1, max_val + 1):
        if result % i == 0:
            sub_possibilities = get_possible_vals_product(result // i, max_val,
                                                          count - 1)
            for p in sub_possibilities:
                if p[0] != -1:
                    new = [i] + p
                    possibilities.append(new)

    if not possibilities:
        return [[-1]]
    return possibilities


def get_possible_vals_quot(result, max_val, count):
    if result < 1:
        return [[-1]]
    if count == 1:
        if max_val >= result:
            return [[result]]
        else:
            return [[-1]]
    possibilities = []
    for i in range(1, max_val + 1):
        if i % result == 0:
            sub_possibilities = get_possible_vals_product(i // result, max_val,
                                                          count - 1)
            for p in sub_possibilities:
                if p[0] != -1:
                    new = [i] + p
                    possibilities.append(new)

    if not possibilities:
        return [[-1]]

    tuples = []
    for x in possibilities:
        tuples += permutations(x)
    return list(set(tuples))
