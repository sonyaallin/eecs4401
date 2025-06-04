#Look for #IMPLEMENT tags in this file.

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
    domain = [i for i in range(1, n + 1)]

    # variable array
    variable_array = make_variables(n, domain)

    # csp
    constraints = []
    for i in range(n):
        for combination in itertools.combinations(variable_array[i], 2):
            constraints.append(make_n_cons(combination, domain, 2))
        for combination in itertools.combinations([row[i] for row in variable_array], 2):
            constraints.append(make_n_cons(combination, domain, 2))

    funpuzz_csp = CSP("binary_ne_grid")
    for row in variable_array:
        for var in row:
            funpuzz_csp.add_var(var)
    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

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
    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]

    # variable array
    variable_array = make_variables(n, domain)

    # csp
    constraints = []
    for i in range(n):
        constraints.append(make_n_cons(variable_array[i], domain, n))
    for j in range(n):
        constraints.append(make_n_cons([row[j] for row in variable_array], domain, n))

    funpuzz_csp = CSP("binary_ne_grid")
    for row in variable_array:
        for var in row:
            funpuzz_csp.add_var(var)
    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

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
    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]

    # variable array
    variable_array = make_variables(n, domain)

    # csp
    constraints = []
    # iterate over all cages
    grid = funpuzz_grid[1:]
    for cage in grid:
        if len(cage) == 2:
            x = cage[0] // 10
            y = cage[0] % 10
            name = variable_array[x-1][y-1].name
            variable_array[x-1][y-1] = Variable(name, [cage[1]])
        else:
            #target value
            target = cage[-2]
            # operation
            op = cage[-1]
            # name
            name = "Cage: ("
            # cells
            cage_cells = []
            cell_domains = []
            for i in range(len(cage) - 2):
                x = cage[i] // 10
                y = cage[i] % 10
                name += variable_array[x-1][y-1].name
                cage_cells.append(variable_array[x-1][y-1])
                cell_domains.append(domain)
            name += ")"
            # constarint obj
            cons = Constraint(name, cage_cells)
            # add sat tuples
            STuples = []
            # Use cartesian product to create an array of tuples with 1 element of each cell's possible value
            # brute force operation on each tuple
            # select only ones that works and add to sat tuples
            for tuple in itertools.product(*cell_domains):
                # +
                if op == 0:
                    if sum(tuple) == target:
                        STuples.append(tuple)
                # -
                elif op == 1:
                    for num in tuple:
                        if num * 2 - sum(tuple) == target:
                            STuples.append(tuple)
                            break
                # /
                elif op == 2:
                    for p in itertools.permutations(tuple):
                        quot = p[0]
                        for num in p[1:]:
                            quot /= num
                        if quot == target:
                            STuples.append(tuple)
                            break
                # *
                elif op == 3:
                    prod = 1
                    for num in tuple:
                        prod *= num
                    if prod == target:
                        STuples.append(tuple)

            cons.add_satisfying_tuples(STuples)
            constraints.append(cons)

    # add nary grid constraint
    for i in range(n):
        constraints.append(make_n_cons(variable_array[i], domain, n))
    for j in range(n):
        constraints.append(make_n_cons([row[j] for row in variable_array], domain, n))

    funpuzz_csp = CSP("funpuzz_csp_model")
    for row in variable_array:
        for var in row:
            funpuzz_csp.add_var(var)
    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array

def make_variables(n, domain):
    # variable array
    variable_array = []
    for i in range(1, n + 1):
        row = []
        for j in range(1, n + 1):
            name = "Variable: (" + str(i) + ", " + str(j) + ")"
            row.append(Variable(name, domain))
        variable_array.append(row)
    return variable_array

def make_n_cons(combination, domain, n):
    name = "Constraint: ("
    for comb in combination:
        name += comb.name
        name += ", "
    name += ")"
    cons = Constraint(name, list(combination))
    # Satisfying tuples
    STuples = list(itertools.permutations(domain, n))
    cons.add_satisfying_tuples(STuples)
    return cons

