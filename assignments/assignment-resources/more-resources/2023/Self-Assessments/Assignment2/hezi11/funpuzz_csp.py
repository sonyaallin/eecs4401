#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import combinations

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
    info = init_var_array(funpuzz_grid)
    variable_array = info[0]
    vars_array = info[1]
    sat_tup = info[2]

    # initialize dict for storing tuple of vars
    vars_comb = dict()
    for var in vars_array:
        vars_comb[var] = []
    for k in vars_comb:
        for var in vars_array:
            if (var.name[0] == k.name[0] or var.name[1] == k.name[1]) \
                    and (k != var):
                vars_comb[k].append(var)

    # initialize scope for constraints
    scopes = []
    for k, v in vars_comb.items():
        for var in v:
            scopes.append((k, var))

    # initialize constraint list
    cons = []
    for pair in scopes:
        c = Constraint("bin_ne", pair)
        c.add_satisfying_tuples(sat_tup)
        cons.append(c)

    # initialize funpuzz_csp
    funpuzz_csp = CSP("binary_ne_grid", vars_array)
    for v in vars_array:
        funpuzz_csp.vars_to_cons[v] = []
    for c in cons:
        funpuzz_csp.add_constraint(c)
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
    info = init_var_array(funpuzz_grid)
    variable_array = info[0]
    vars_array = info[1]

    sizeof_g = funpuzz_grid[0][0]

    # find sat_tup
    nums = [i for i in range(1, sizeof_g+1)]
    sat_tup = []
    for i in combinations(nums, sizeof_g):
        sat_tup.append(i)

    # find scope
    scopes = []
    # row
    for v in variable_array:
        scopes.append(v)
    # column
    col = []
    for i in range(sizeof_g):
        col.append([row[i] for row in variable_array])
    for item in col:
        scopes.append(item)

    # initialize cons list
    cons = []
    for lst in scopes:
        c = Constraint("n_ary_ad", lst)
        c.add_satisfying_tuples(sat_tup)
        cons.append(c)

    funpuzz_csp = CSP("nary_ad_grid", vars_array)
    for v in vars_array:
        funpuzz_csp.vars_to_cons[v] = []
    for c in cons:
        funpuzz_csp.add_constraint(c)
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
    grid_csp, variable_array = \
        nary_ad_grid(funpuzz_grid)[0], nary_ad_grid(funpuzz_grid)[1]
    sizeof_g = funpuzz_grid[0][0]

    cons = []
    # iterate through cages
    for cages in funpuzz_grid:
        if len(cages) == 1 or len(cages) == 2:
            continue
        sign = cages[-1]
        res = cages[-2]
        nums = [i for i in range(1, sizeof_g+1)]
        num_cell = len(cages) - 2
        sat_tup = []
        if sign == 0:
            for i in combinations(nums, num_cell):
                if sum(i) == res:
                    sat_tup.append(i)
        if sign == 3:
            for i in combinations(nums, num_cell):
                if product(i) == res:
                    sat_tup.append(i)
        if sign == 1:
            for i in combinations(nums, num_cell):
                for j in combinations(i, len(i)):
                    if difference(j) == res:
                        sat_tup.append(j)
        if sign == 2:
            for i in combinations(nums, num_cell):
                for j in combinations(i, len(i)):
                    if division(j) == res:
                        sat_tup.append(j)
        domain = []
        for tup in sat_tup:
            for i in tup:
                if i not in domain:
                    domain.append(i)
        scope = []
        vars_array = []
        for i in range(len(variable_array)):
            for j in range(len(variable_array[i])):
                vars_array.append(variable_array[i][j])
        for i in range(0, len(cages)-2):
            for v in vars_array:
                if v.name == str(cages[i]):
                    scope.append(v)

        c = Constraint("cage constraint", scope)
        c.add_satisfying_tuples(sat_tup)
        cons.append(c)

    for c in cons:
        grid_csp.add_constraint(c)
    return grid_csp, variable_array


def init_var_array(funpuzz_grid):
    # determine the size of the grid
    size_of_g = funpuzz_grid[0][0]

    # find pre-defined cells, if there is any
    var_set_cell = []
    val_set_cell = []
    for lst in funpuzz_grid:
        if len(lst) == 2:
            var_set_cell.append(lst[0])
            val_set_cell.append(lst[1])

    # create the correct size of variable_array
    variable_array = [[] for _ in range(size_of_g)]

    # create a flat variable array for initializing funpuzz_csp
    vars_array = []

    # initialize satisfying tuple
    sat_tup = []

    # append variables to variable_array
    # create sat_tuple
    for i in range(1, size_of_g+1):
        for j in range(1, size_of_g+1):
            var_name = i*10 + j
            # if current cell has set value
            if var_name in var_set_cell:
                var = Variable(str(var_name), [])
                val = var_set_cell.index(var_name)
                var.assign(val)
                variable_array[i-1].append(var)
                vars_array.append(var)
                continue
            var = Variable(str(var_name), [i for i in range(1, size_of_g+1)])
            variable_array[i-1].append(var)
            vars_array.append(var)

            if i != j:
                sat_tup.append((i, j))

    return variable_array, vars_array, sat_tup


def product(lst):
    result = 1
    for x in lst:
        result = result * x
    return result


def difference(lst):
    result = 0
    for x in lst:
        result = result - x
    return result


def division(lst):
    result = 1
    for x in lst:
        result = result / x
    return result


board = [[3], [11, 21, 3, 0], [12, 22, 2, 1], [13, 23, 33, 6, 3], [31, 32, 5, 0]]
res_csp, variables = binary_ne_grid(board)
print(res_csp.name)
print(res_csp.vars)
print(res_csp.cons)
print(res_csp.vars_to_cons)
