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
    csp = CSP("Binary_NE_Grid")
    dimension = funpuzz_grid[0][0]
    domain = range(1, dimension+1)

    variable_grid = make_var_grid(csp, dimension)

    boxes = itertools.product(domain, repeat=2)
    for b in boxes:
        var1 = variable_grid[b[0]-1][b[1]-1]
        for i in range(b[0], dimension):
            var2 = variable_grid[i][b[1]-1]
            cons = Constraint("({},{}) != ({},{})".format(
                b[0], b[1], i+1, b[1]), (var1, var2))
            sat_tuples = itertools.permutations(domain, 2)
            cons.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(cons)

        for i in range(b[1], dimension):
            var2 = variable_grid[b[0]-1][i]
            cons = Constraint("({},{}) != ({},{})".format(
                b[0], b[1], b[0], i+1), (var1, var2))
            sat_tuples = itertools.permutations(domain, 2)
            cons.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(cons)

    # Creating unary constraint so that prop_FC can work
    unary_cons = Constraint("Unary Constraint", [variable_grid[0][0]])
    unary_sat_tups = []
    for val in domain:
        unary_sat_tups.append([val])
    unary_cons.add_satisfying_tuples(unary_sat_tups)
    csp.add_constraint(unary_cons)

    return csp, variable_grid


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
    csp = CSP("Nary_AD_Grid")
    dimension = funpuzz_grid[0][0]
    domain = range(1, dimension+1)

    variable_grid = make_var_grid(csp, dimension)

    for i in range(dimension):
        row_cons_list = []
        col_cons_list = []
        for j in range(dimension):
            row_cons_list.append(variable_grid[i][j])
            col_cons_list.append(variable_grid[j][i])
        sat_tuples = itertools.permutations(domain, dimension)
        row_cons = Constraint("{}-row constraint".format(i+1), row_cons_list)
        row_cons.add_satisfying_tuples(sat_tuples)
        sat_tuples = itertools.permutations(domain, dimension)
        col_cons = Constraint("{}-col constraint".format(i+1), col_cons_list)
        col_cons.add_satisfying_tuples(sat_tuples)

        csp.add_constraint(row_cons)
        csp.add_constraint(col_cons)

    # Creating unary constraint so that prop_FC can work
    unary_cons = Constraint("Unary Constraint", [variable_grid[0][0]])
    unary_sat_tups = []
    for val in domain:
        unary_sat_tups.append([val])
    unary_cons.add_satisfying_tuples(unary_sat_tups)
    csp.add_constraint(unary_cons)

    return csp, variable_grid


def make_var_grid(csp, dimension):
    variable_grid = []
    domain = range(1, dimension+1)
    for i in range(dimension):
        row = []
        for j in range(dimension):
            var = Variable("({},{})".format(i+1, j+1), domain)
            csp.add_var(var)
            row.append(var)
        variable_grid.append(row)
    return variable_grid


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

    csp, var_grid = binary_ne_grid(funpuzz_grid)

    dimension = funpuzz_grid[0][0]
    domain = range(1, dimension+1)
    cages = funpuzz_grid[1:]

    for i in range(len(cages)):
        cage = cages[i]
        con_vars = []
        if len(cage) == 2:
            row = cage[0] // 10
            col = cage[0] % 10
            con_vars.append(var_grid[row-1][col-1])
            target = cage[1]
            sat_tuples = [tuple(target)]
        else:
            for coor in cage[:-2]:
                row = coor // 10
                col = coor % 10
                con_vars.append(var_grid[row-1][col-1])

            target = cage[-2]
            operation = cage[-1]

            all_combinations = itertools.combinations_with_replacement(
                domain, len(cage[:-2]))

            sat_tuples = []
            for comb in all_combinations:
                if satisfies(target, comb, operation):
                    sat_tuples.extend(itertools.permutations(comb, len(comb)))

        cons = Constraint("Cage:{}".format(i), con_vars)
        cons.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(cons)
    return csp, var_grid


def satisfies(TARGET, combinations, operation):
    '''
    ### HELPER FUNCTION ###
    Checks if any permutation of values in combinations matches
    the TARGET after performing 'operation' on them.
    '''
    for i in range(len(combinations)):
        # initialise total to have value of combinations[i]
        total = combinations[i]
        for j in range(len(combinations)):
            if i != j:
                total = do_op(total, combinations[j], operation)
        if total == TARGET:
            return True
    return False


def do_op(total, element, operation):
    '''
    ### HELPER FUNCTION ###
    Performs a corresponding operation (0='+', 1='-', 2='/', 3='*')
    on total by the value of element and returns the new total
    '''
    if operation == 0:
        total += element
    elif operation == 1:
        total -= element
    elif operation == 2:
        total /= element
    else:
        total *= element
    return total
