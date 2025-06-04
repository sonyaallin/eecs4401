'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from functools import reduce
from itertools import permutations

def create_variables(csp, grid_size):
    """Creates a Variable object for each cell in a FunPuzz with the given
    grid size. Returns a list of lists containing the created variables, where
    the element i,j represents cell i,j.
    """
    vars = []
    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            name = "V{}{}".format(i+1, j+1)
            domain = list(range(1, grid_size+1))
            var = Variable(name, domain)
            csp.add_var(var)
            row.append(var)
        vars.append(row)
    return vars

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
    funpuzz_csp = CSP("FunPuzz (binary not-equal)")
    grid_size = funpuzz_grid[0][0]
    variable_array = create_variables(funpuzz_csp, grid_size)

    # List of satisfying tuples for binary not-equal constraints
    sat_tuples = list(permutations(range(1, grid_size+1), 2))

    # Create binary constraints for rows
    for i in range(grid_size):
        for j in range(grid_size):
            for k in range(grid_size):
                if j != k:
                    name = "{}{}-{}{}".format(i+1, j+1, i+1, k+1)
                    scope = [variable_array[i][j], variable_array[i][k]]
                    con = Constraint(name, scope)
                    con.add_satisfying_tuples(sat_tuples)
                    funpuzz_csp.add_constraint(con)

    # Create binary constraints for columns
    for j in range(grid_size):
        for i in range(grid_size):
            for k in range(grid_size):
                if i != k:
                    name = "{}{}-{}{}".format(i+1, j+1, k+1, j+1)
                    scope = [variable_array[i][j], variable_array[k][j]]
                    con = Constraint(name, scope)
                    con.add_satisfying_tuples(sat_tuples)
                    funpuzz_csp.add_constraint(con)

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
    funpuzz_csp = CSP("FunPuzz (n-ary all-different)")
    grid_size = funpuzz_grid[0][0]
    variable_array = create_variables(funpuzz_csp, grid_size)

    # List of satisfying tuples for n-ary all-different constraints
    sat_tuples = list(permutations(range(1, grid_size+1)))

    # Create n-ary constraints for rows
    for i in range(grid_size):
        scope = []
        for j in range(grid_size):
            scope.append(variable_array[i][j])
        name = "Row{}".format(i+1)
        con = Constraint(name, scope)
        con.add_satisfying_tuples(sat_tuples)
        funpuzz_csp.add_constraint(con)

    # Create n-ary constraints for columns
    for j in range(grid_size):
        scope = []
        for i in range(grid_size):
            scope.append(variable_array[i][j])
        name = "Col{}".format(j+1)
        con = Constraint(name, scope)
        con.add_satisfying_tuples(sat_tuples)
        funpuzz_csp.add_constraint(con)

    return funpuzz_csp, variable_array

def recursive_get_tuples(t, n, num_vars, grid_size, tuples):
    """Recursive function that identifies all possible tuples for a constraint
    using the given number of variables and grid size.
    """
    if n == num_vars:
        for val in range(1, grid_size+1):
            tuples.append(t + (val,))
    else:
        for val in range(1, grid_size+1):
            recursive_get_tuples(t + (val,), n+1, num_vars, grid_size, tuples)


def add_to_target(vals, target):
    """Returns true if the values in vals add to the given target.
    """
    return sum(vals) == target

def sub_to_target(vals, target):
    """Returns true if the values in vals subtract to the given target.
    Note that subtraction is not commutative, so all permutations of vals is
    checked.
    """
    op_func = lambda x, y : x - y
    val_perms = list(permutations(vals))
    for vals in val_perms:
        if reduce(op_func, vals) == target:
            return True
    return False

def div_to_target(vals, target):
    """Returns true if the values in vals divide to the given target.
    Note that division is not commutative, so all permutations of vals is
    checked.
    """
    op_func = lambda x, y : x / y
    val_perms = list(permutations(vals))
    for vals in val_perms:
        if reduce(op_func, vals) == target:
            return True
    return False

def mul_to_target(vals, target):
    """Returns true if the values in vals multiply to the given target.
    """
    op_func = lambda x, y : x * y
    return reduce(op_func, vals) == target

def identify_cage_con_sat_tuples(num_vars, target, op, grid_size):
    """Returns the satisfying tuples for a cage constraint, given the number
    of variables, target value, and operation id of the constraint, and the
    grid size of the FunPuzz.
    """
    # Get all possible tuples
    tuples = []
    recursive_get_tuples((), 1, num_vars, grid_size, tuples)

    # Curry the corresponding function so it can be used with filter()
    if op == 0:
        filter_func = lambda x : add_to_target(x, target)
    elif op == 1:
        filter_func = lambda x : sub_to_target(x, target)
    elif op == 2:
        filter_func = lambda x : div_to_target(x, target)
    else:
        filter_func = lambda x : mul_to_target(x, target)
    
    # Filter tuples to get satisfying tuples
    return list(filter(filter_func, tuples))

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
    funpuzz_csp = CSP("FunPuzz")
    grid_size = funpuzz_grid[0][0]
    cage_cons = funpuzz_grid[1:]
    variable_array = create_variables(funpuzz_csp, grid_size)

    # List of satisfying tuples for n-ary all-different constraints
    sat_tuples = list(permutations(range(1, grid_size+1)))

    # Create n-ary constraints for rows
    for i in range(grid_size):
        scope = []
        for j in range(grid_size):
            scope.append(variable_array[i][j])
        name = "Row{}".format(i+1)
        con = Constraint(name, scope)
        con.add_satisfying_tuples(sat_tuples)
        funpuzz_csp.add_constraint(con)

    # Create n-ary constraints for columns
    for j in range(grid_size):
        scope = []
        for i in range(grid_size):
            scope.append(variable_array[i][j])
        name = "Col{}".format(j+1)
        con = Constraint(name, scope)
        con.add_satisfying_tuples(sat_tuples)
        funpuzz_csp.add_constraint(con)

    # Create cage constraints
    for id, cage_con in enumerate(cage_cons):
        vars = cage_con[:-2]
        target = cage_con[-2]
        op = cage_con[-1]

        scope = []
        for var in vars:
            i = (var // 10) - 1
            j = (var % 10) - 1
            scope.append(variable_array[i][j])

        sat_tuples = identify_cage_con_sat_tuples(len(vars), target, op, grid_size)

        name = "Cage{}".format(id+1)
        con = Constraint(name, scope)
        con.add_satisfying_tuples(sat_tuples)
        funpuzz_csp.add_constraint(con)

    return funpuzz_csp, variable_array
