# Look for #IMPLEMENT tags in this file.

"""
Construct and return funpuzz CSP models.
"""
from cspbase import *
from functools import reduce
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
    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]

    # create variables for model
    var_array = create_variables(domain)
    csp = CSP("binary funpuzz", list(it.chain.from_iterable(var_array)))

    # create scope pairs for binary constraints
    constraints = []
    variables = csp.get_all_vars()
    for i in range(n):
        # create row constraints
        temp = i * n
        row_vars = variables[temp:temp + n]
        constraints.extend(list(it.combinations(row_vars, 2)))

        # create column constraints
        col_vars = [variables[j * n + i] for j in range(n)]
        constraints.extend(list(it.combinations(col_vars, 2)))

    # Create Constraint objects with satisfying tuples and add to csp model
    i = 1
    for c in constraints:
        con = Constraint("C{:d}".format(i), c)
        con.add_satisfying_tuples(list(it.permutations(domain, 2)))
        csp.add_constraint(con)
        i += 1

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
    domain = [i for i in range(1, n + 1)]

    # create variables for csp model
    var_array = create_variables(domain)
    csp = CSP("n-ary funpuzz", list(it.chain.from_iterable(var_array)))

    # create n-ary Constraint objects for each row and column
    variables = csp.get_all_vars()
    for i in range(n):
        sat_tuples = list(it.permutations(domain))

        # create row constraints
        temp = i * n
        row_vars = variables[temp:temp + n]
        c = Constraint("C{:d}".format(2*i), row_vars)
        c.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(c)

        # create column constraints
        col_vars = [variables[j * n + i] for j in range(n)]
        c = Constraint("C{:d}".format(2*i+1), col_vars)
        c.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(c)

    return csp, var_array


def create_variables(domain):
    """Create the variables for the csp model"""
    n = len(domain)
    var_array = []
    for i in range(1, n + 1):
        row = []
        for j in range(1, n + 1):
            name = "{:d}{:d}".format(i, j)
            var = Variable(name, domain)
            row.append(var)
        var_array.append(row)
    return var_array


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
    # Get n-ary all-diff constraint model to add to
    csp, var_array = nary_ad_grid(funpuzz_grid)

    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]
    operation = {0: '+', 1: '-', 2: '/', 3: '*'}

    con_num = 1
    for cage in funpuzz_grid[1:]:
        if len(cage) == 2:
            # Assign values that are fixed
            var = str(cage[0])
            i = int(var[0])
            j = int(var[1])
            val = cage[1]
            var_array[i-1][j-1].assign(val)
        else:
            # Extract operation, target and scope from cage and instantiate new constraint
            op = operation[cage[-1]]
            target = cage[-2]
            scope_int = cage[:-2]

            # Get variables for cells defined in cage constraint
            scope = []
            for s in scope_int:
                temp = str(s)
                i = int(temp[0])
                j = int(temp[1])
                var = var_array[i-1][j-1]
                scope.append(var)
            con = Constraint(("C{:d}"+op).format(con_num), scope)

            # Add tuples that satisfy constraint
            orders_possible = set(it.combinations_with_replacement(domain, len(scope)))
            sat_tups = get_sat_tuples(op, target, orders_possible)
            con.add_satisfying_tuples(sat_tups)

            csp.add_constraint(con)
        con_num += 1

    return csp, var_array


def get_sat_tuples(op, target, possibles):
    """Return the list of tuples from possibles that satisfy using op
       to get the target value"""
    satisfying = []
    for p in possibles:
        # Order of assignment does not matter so need to add all permutations
        perms = set(it.permutations(p))
        if op == '+':
            if sum(p) == target:
                satisfying.extend(perms)
        elif op == '*':
            if reduce(lambda x, y: x*y, p) == target:
                satisfying.extend(perms)
        else:
            # Order of operation affects answer in division and subtraction so
            # check each permutation to ensure if any succeed
            for t in perms:
                if op == '/':
                    if reduce(lambda x, y: x/y, t) == target:
                        satisfying.extend(perms)
                        break
                else:
                    if reduce(lambda x, y: x-y, t) == target:
                        satisfying.extend(perms)
                        break
    return satisfying
