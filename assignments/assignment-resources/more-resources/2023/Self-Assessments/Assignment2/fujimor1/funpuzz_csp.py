# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import numpy as np
from itertools import combinations, permutations, product


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
    # initialize variables
    dim = funpuzz_grid[0][0]
    domain = [k for k in range(1, dim+1)]
    vars = np.zeros((dim, dim)).tolist()
    for i in range(dim):
        for j in range(dim):
            vars[i][j] = Variable("v" + str(i+1) + str(j+1), domain)

    # obtain binary variable combinations
    var_comb = []
    for i in range(dim):
        var_comb += list(combinations(vars[i], 2))
        var_comb += list(combinations([v[i] for v in vars], 2))

    # satisfying tuples
    tuples = []
    for i in domain:
        for j in domain:
            if i != j:
                tuples.append((i, j))

    # initialize constraints and csp
    csp = CSP('csp', sum(vars, []))
    for i, v in enumerate(var_comb):
        con = Constraint("c" + str(i+1), v)
        con.add_satisfying_tuples(tuples)
        csp.add_constraint(con)

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
    # initialize variables
    dim = funpuzz_grid[0][0]
    domain = [k for k in range(1, dim+1)]
    vars = np.zeros((dim, dim)).tolist()
    for i in range(dim):
        for j in range(dim):
            vars[i][j] = Variable("v" + str(i+1) + str(j+1), domain)

    # obtain n-ary variable combinations
    var_comb = []
    for i in range(dim):
        var_comb += [vars[i]]
        var_comb += [[v[i] for v in vars]]

    # satisfying tuples
    tuples = list(permutations(domain, dim))

    # initialize constraints and csp
    csp = CSP('csp', sum(vars, []))
    for i, v in enumerate(var_comb):
        con = Constraint("c" + str(i+1), v)
        con.add_satisfying_tuples(tuples)
        csp.add_constraint(con)

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
    # initialize csp using nary_ad_grid() function
    csp, variable_array = nary_ad_grid(funpuzz_grid)
    csp_vars = csp.get_all_vars()
    dim = funpuzz_grid[0][0]

    # iterate over a list of cages
    for i, cage in enumerate(funpuzz_grid[1:]):
        # special case: when len(cage) = 2
        if len(cage) == 2:
            # obtain a variable object
            for v in csp_vars:
                if v.name == "v" + str(cage[0]):
                    break
            # create a new cage constraint
            con = Constraint("cage" + str(i+1), [v])
            con.add_satisfying_tuples(((cage[1],),))
            csp.add_constraint(con)
            continue
        
        # other cases

        # obtain target and operation
        target = cage[-2]
        operation = cage[-1]

        # find Variable objects for this cage
        vars = []
        for cell in cage[:-2]:
            for v in csp_vars:
                if v.name == "v" + str(cell):
                    vars.append(v)
                    break
        
        # create a new cage constraint
        con = Constraint("cage" + str(i+1), vars)
        tuples = get_cage_tuples(len(vars), target, operation, dim)
        con.add_satisfying_tuples(tuples)
        csp.add_constraint(con)
    
    return csp, variable_array


def get_cage_tuples(var_num, target, operation, dim):
    """Helper function of funpuzz_csp_model()
    Obtain all tuples that satisfy the cage constraint
    """
    domain = [i for i in range(1, dim+1)]
    candidates = list(product(domain, repeat=var_num))
    tuples = []
    for cand in candidates:
        if operation == 0:
            if sum(cand) == target:
                tuples.append(cand)
        elif operation == 1:
            for i in range(var_num):
                if 2*cand[i] - sum(cand) == target:
                    tuples.append(cand)
                    break
        elif operation == 2:
            for i in range(var_num):
                if int(cand[i]**2 / np.prod(cand)) == target:
                    tuples.append(cand)
                    break
        else:
            if np.prod(cand) == target:
                tuples.append(cand)
    return tuples
