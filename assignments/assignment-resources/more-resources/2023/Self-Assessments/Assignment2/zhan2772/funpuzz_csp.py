# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools


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
    n = funpuzz_grid[0][0]
    csp = CSP('funpuzz')
    vars = []
    for i in range(n):
        var_lst = []
        for j in range(n):
            var = Variable(str(i) + str(j), list(range(1, n + 1)))
            var_lst.append(var)
            csp.add_var(var)
        vars.append(var_lst)

    satisfying_tuples = []
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if j != i:
                satisfying_tuples.append((i, j))

    for i in range(n):
        for j in range(n):
            v = vars[i][j]
            row = vars[i]
            for o in row:
                if o != v:
                    c = Constraint(v.name + o.name, [v, o])
                    c.add_satisfying_tuples(satisfying_tuples)
                    csp.add_constraint(c)

            for k in range(n):
                o = vars[k][j]
                if o != v:
                    c = Constraint(v.name + o.name, [v, o])
                    c.add_satisfying_tuples(satisfying_tuples)
                    csp.add_constraint(c)

    return csp, vars


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
    csp = CSP('funpuzz')
    vars = []
    for i in range(n):
        row = []
        for j in range(n):
            var = Variable(str(i) + str(j), list(range(1, n + 1)))
            row.append(var)
            csp.add_var(var)
        vars.append(row)

    satisfying_tuples = set(itertools.permutations(range(1, n + 1), n))

    for i in range(n):
        row = vars[i]
        c = Constraint(f'row-{i}', row)
        c.add_satisfying_tuples(satisfying_tuples)
        csp.add_constraint(c)

        col = []
        for j in range(n):
            col.append(vars[j][i])

        c = Constraint(f'col-{i}', col)
        c.add_satisfying_tuples(satisfying_tuples)
        csp.add_constraint(c)

    return csp, vars


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
    n = funpuzz_grid[0][0]
    csp, vars = nary_ad_grid(funpuzz_grid)

    for cage in funpuzz_grid[1:]:
        cells = [vars[cell // 10 - 1][cell % 10 - 1] for cell in cage[:-2]]
        target = cage[-2]
        op = cage[-1]
        satisfying_tuples = []

        for tup in list(
                itertools.permutations(list(range(1, n + 1)) * len(cells),
                                       len(cells))):
            for vals in list(itertools.permutations(tup, len(tup))):
                y = vals[0]
                for val in vals[1:]:
                    if op == 0:
                        y += val
                    elif op == 1:
                        y -= val
                    elif op == 2:
                        y /= val
                    else:
                        y *= val
                if y == target:
                    satisfying_tuples.append(tup)
                    break

        c = Constraint('cage', cells)
        c.add_satisfying_tuples(satisfying_tuples)
        csp.add_constraint(c)

    return csp, vars
