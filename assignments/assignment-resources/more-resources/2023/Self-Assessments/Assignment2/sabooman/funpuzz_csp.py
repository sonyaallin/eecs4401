#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools as it


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
    dimension = funpuzz_grid[0][0]
    result = []
    csp = CSP("binary_model")

    for i in range(dimension):  # row
        val = []
        for j in range(dimension):  # column
            var = Variable(str(i+1) + str(j+1), range(1, dimension+1))
            csp.add_var(var)
            val.append(var)
        result.append(val)

    con = Constraint("con_first", [result[0][0]])
    con.add_satisfying_tuples(it.permutations(range(1, dimension+1), 1))
    csp.add_constraint(con)

    for vars in result:   # rows
        combos = it.combinations(vars, 2)
        for combo in combos:
            con = Constraint("con", list(combo))
            con.add_satisfying_tuples(it.permutations(range(1, dimension+1), 2))
            csp.add_constraint(con)

    for i in range(dimension):  # columns
        vars = []
        for j in range(dimension):
            vars.append(result[j][i])
        combos = it.combinations(vars, 2)
        for combo in combos:
            con = Constraint("con", list(combo))
            con.add_satisfying_tuples(it.permutations(range(1, dimension+1), 2))
            csp.add_constraint(con)

    return csp, result


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
    dimension = funpuzz_grid[0][0]
    result = []
    csp = CSP("nary_model")

    for i in range(dimension):  # row
        val = []
        for j in range(dimension):  # column
            var = Variable(str(i+1) + str(j+1), range(1, dimension+1))
            csp.add_var(var)
            val.append(var)
        result.append(val)

    con = Constraint("con_first", [result[0][0]])
    con.add_satisfying_tuples(it.permutations(range(1, dimension+1), 1))
    csp.add_constraint(con)

    for row in result:
        con = Constraint("con", row)  # columns must be uniques in each row
        con.add_satisfying_tuples(it.permutations(range(1, dimension+1), dimension))
        csp.add_constraint(con)

    for col in range(0, dimension): # columns
        val = []
        for row in range(0, dimension):
            val.append(result[row][col])
        con = Constraint("con", val)  # columns must be uniques in each row
        con.add_satisfying_tuples(it.permutations(range(1, dimension+1), dimension))
        csp.add_constraint(con)

    return csp, result


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

    dimension = funpuzz_grid[0][0]
    n_ary, result = binary_ne_grid(funpuzz_grid)

    for i in range(1, len(funpuzz_grid)): # constrains for grids
        global op
        global tot
        vars = []

        if len(funpuzz_grid[i]) == 2:
            con = Constraint("con", get_variable(result, funpuzz_grid[i][0]))
            con.add_satisfying_tuples((funpuzz_grid[i][1]))
            n_ary.add_constraint(con)

        for var in range(len(funpuzz_grid[i]) - 2):
            variable = get_variable(result, funpuzz_grid[i][var])
            vars.append(variable)

        op = funpuzz_grid[i][len(funpuzz_grid[i]) - 1]
        tot = funpuzz_grid[i][len(funpuzz_grid[i]) - 2]
        con = Constraint("con", vars)
        permutations = it.combinations_with_replacement(range(1, dimension+1), len(vars))
        filtered = list(filter(total_nary, permutations))
        res = []
        for fit in filtered:
            res.extend(it.permutations(fit, len(fit)))
        con.add_satisfying_tuples(res)
        n_ary.add_constraint(con)
    return n_ary, result


def get_variable(vars, position):
    """return the variable from the list of list vars, as per the position from
    fungrid cages"""
    j = (position % 10) - 1
    i = (position // 10) - 1
    return vars[i][j]


def total_nary(tup):
    """return whether a permutation satisfies an operation op by giving
    the result as tot"""
    tup = list(tup)
    if op == 1:
        return check(it.permutations(tup, len(tup)))
    elif op == 2:
        return check(it.permutations(tup, len(tup)))
    ans = tup.pop(0)
    if op == 0:
        while len(tup) != 0:
            ans += tup.pop(0)
    elif op == 3:
        while len(tup) != 0:
            ans *= tup.pop(0)
    return ans == tot


def check(permutations):
    for tup in permutations:
        tup = list(tup)
        ans = tup.pop(0)
        while len(tup) != 0:
            if op == 1:
                ans -= tup.pop(0)
            elif op == 2:
                ans = ans / tup.pop(0)
        if ans == tot:
            return True
    return False
