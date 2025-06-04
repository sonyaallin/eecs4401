#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools


def get_vars(variable_array, funpuzz_csp, vals, n):
    for r in range(n):
        variable_array.append([])
        for c in range(n):
            name = str(r+1) + ',' + str(c+1)
            v = Variable(name, vals)
            funpuzz_csp.add_var(v)
            variable_array[r].append(v)


def binary_all_difs(variable_array, funpuzz_csp, satisfy_tups, n):
    for k in range(n):
        for i in range(n):
            for j in range(i+1, n):
                name = "col: " + variable_array[i][k].name + ' and ' + variable_array[j][k].name
                cons = Constraint(name, [variable_array[i][k], variable_array[j][k]])
                cons.add_satisfying_tuples(satisfy_tups)
                funpuzz_csp.add_constraint(cons)

                name = "row: " + variable_array[i][k].name + ' and ' + variable_array[j][k].name
                cons = Constraint(name, [variable_array[k][i], variable_array[k][j]])
                cons.add_satisfying_tuples(satisfy_tups)
                funpuzz_csp.add_constraint(cons)


def nary_all_difs(variable_array, funpuzz_csp, satisfy_tups, n):
    for i in range(n):
        name = "col: " + str(i)
        cons = Constraint(name, [variable_array[k][i] for k in range(n)])
        cons.add_satisfying_tuples(satisfy_tups)
        funpuzz_csp.add_constraint(cons)

        name = "row: " + str(i)
        cons = Constraint(name, [variable_array[i][k] for k in range(n)])
        cons.add_satisfying_tuples(satisfy_tups)
        funpuzz_csp.add_constraint(cons)


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
    funpuzz_csp = CSP("binary grid-only FunPuzz")
    variable_array = []
    n = funpuzz_grid[0][0]
    satisfy_tups = [tup for tup in itertools.permutations(range(1, n+1), 2)]
    vals = [i for i in range(1, n+1)]

    get_vars(variable_array, funpuzz_csp, vals, n)

    binary_all_difs(variable_array, funpuzz_csp, satisfy_tups, n)

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
    funpuzz_csp = CSP("n-ary grid-only FunPuzz")
    variable_array = []
    n = funpuzz_grid[0][0]
    satisfy_tups = [tup for tup in itertools.permutations(range(1, n+1), n)]
    vals = [i for i in range(1, n+1)]

    get_vars(variable_array, funpuzz_csp, vals, n)

    nary_all_difs(variable_array, funpuzz_csp, satisfy_tups, n)

    return funpuzz_csp, variable_array


def add(tup, target):
    acc = tup[0]
    for i in tup[1:]:
        acc += i
    return acc == target


def mult(tup, target):
    acc = tup[0]
    for i in tup[1:]:
        acc *= i
    return acc == target


def sub(tup, target):
    for t in itertools.permutations(tup):
        acc = t[0]
        for i in t[1:]:
            acc -= i
        if acc == target:
            return True
    return False


def div(tup, target):

    for t in itertools.permutations(tup):
        acc = t[0]
        for i in t[1:]:
            acc /= i
        if acc == target:
            return True

    return False


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
    operation = None
    funpuzz_csp = CSP("funpuzz")
    variable_array = []
    n = funpuzz_grid[0][0]
    satisfy_tups = [tup for tup in itertools.permutations(range(1, n+1), 2)]
    vals = [i for i in range(1, n+1)]

    get_vars(variable_array, funpuzz_csp, vals, n)

    binary_all_difs(variable_array, funpuzz_csp, satisfy_tups, n)

    for cage in funpuzz_grid[1:]:
        vals = []
        target, op = cage[-2], cage[-1]
        if op == 0:
            operation = add
        elif op == 1:
            operation = sub
        elif op == 3:
            operation = mult
        elif op == 2:
            operation = div

        for i in range(len(cage)-2):
            cell = str(cage[i])
            x, y = int(cell[0])-1, int(cell[1])-1
            vals.append(variable_array[x][y])

        name = "Constraint " + str(target) + ' ' + str(op)
        cons = Constraint(name, vals)
        satisfy_tups = [tup for tup in itertools.product(range(1, n+1), repeat = len(vals)) if operation(tup, target)]
        cons.add_satisfying_tuples(satisfy_tups)
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array


