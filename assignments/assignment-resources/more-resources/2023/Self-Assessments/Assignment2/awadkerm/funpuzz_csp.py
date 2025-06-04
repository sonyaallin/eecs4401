"""
Construct and return funpuzz CSP models.
"""
import itertools
import operator

from cspbase import *
import numpy as np

OPERATORS = [operator.add, operator.sub, operator.truediv, operator.mul]
OPERATOR_SYMBOLS = [' + ', ' - ', ' / ', ' * ']


def binary_ne_grid(funpuzz_grid):
    """
    A model of a funpuzz grid (without cage constraints) built using only binary all-different
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
    default_range = tuple(range(1, funpuzz_grid[0][0] + 1))
    variables = [Variable(f'{i}{j}', default_range) for i in default_range for j in default_range]

    csp = CSP("binary_ne_grid", variables)
    variables = np.asarray(variables).reshape((funpuzz_grid[0][0], funpuzz_grid[0][0]))

    permutations = list(itertools.permutations(default_range, 2))

    for i in default_range:
        for combination in itertools.combinations(default_range, 2):
            row_scope = [variables[i - 1][combination[0] - 1], variables[i - 1][combination[1] - 1]]
            row_cons = Constraint(f'{i}{combination[0]} != {i}{combination[1]}', row_scope)
            row_cons.add_satisfying_tuples(permutations)
            csp.add_constraint(row_cons)

            col_scope = [variables[combination[0] - 1][i - 1], variables[combination[1] - 1][i - 1]]
            col_cons = Constraint(f'{combination[0]}{i} != {combination[1]}{i}', col_scope)
            col_cons.add_satisfying_tuples(permutations)
            csp.add_constraint(col_cons)

    return csp, variables.tolist()


def nary_ad_grid(funpuzz_grid):
    """
    A model of a funpuzz grid (without cage constraints) built using only n-ary all-different
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
    default_range = tuple(range(1, funpuzz_grid[0][0] + 1))
    variables = [Variable(f'{i}{j}', default_range) for i in default_range for j in default_range]

    csp = CSP("nary_ad_grid", variables)
    variables = np.asarray(variables).reshape((funpuzz_grid[0][0], funpuzz_grid[0][0]))

    permutations = list(itertools.permutations(default_range, funpuzz_grid[0][0]))

    for i in default_range:
        row_scope = variables[i - 1]
        row_cons = Constraint(f'row {i} all different', row_scope)
        row_cons.add_satisfying_tuples(permutations)
        csp.add_constraint(row_cons)

        col_scope = variables[:, i - 1]
        col_cons = Constraint(f'column {i} all different', col_scope)
        col_cons.add_satisfying_tuples(permutations)
        csp.add_constraint(col_cons)

    return csp, variables.tolist()


def funpuzz_csp_model(funpuzz_grid):
    """
    A model built using your choice of (1) binary binary not-equal, or (2) n-ary all-different
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
    csp, variables = binary_ne_grid(funpuzz_grid)
    csp.name = 'funpuzz'

    default_range = tuple(range(1, funpuzz_grid[0][0] + 1))

    for cage in funpuzz_grid[1:]:
        if len(cage) == 2:
            i, j = (cage[0] // 10) - 1, (cage[0] % 10) - 1
            variables[i][j].dom = [cage[1]]
            variables[i][j].curdom = [True]
        else:
            cells = []
            for cell in cage[:-2]:
                cells += [variables[(cell // 10) - 1][(cell % 10) - 1]]

            cons = Constraint(OPERATOR_SYMBOLS[cage[-1]].join(str(i) for i in cage[:-2]) + f' = {cage[-2]}', cells)
            satisfying_tuples = []

            if cage[-1] in [1, 2]:
                permutations = set(itertools.permutations(default_range, len(cells)))

                while permutations:
                    permutation = permutations.pop()

                    total = permutation[0]
                    for val in permutation[1:]:
                        total = OPERATORS[cage[-1]](total, val)

                    if total == cage[-2]:
                        valid_permutations = itertools.permutations(permutation, len(cells))
                        for valid_permutation in valid_permutations:
                            if valid_permutation in permutations:
                                permutations.remove(valid_permutation)

                            satisfying_tuples += [valid_permutation]
            else:
                add_flag = cage[-1] == 0
                combinations = itertools.combinations_with_replacement(default_range[:cage[-2] - add_flag], len(cells))

                for combination in combinations:
                    total = combination[0]
                    for val in combination[1:]:
                        total = OPERATORS[cage[-1]](total, val)

                    if total == cage[-2]:
                        satisfying_tuples += itertools.permutations(combination, len(cells))

            cons.add_satisfying_tuples(satisfying_tuples)
            csp.add_constraint(cons)

    return csp, variables
