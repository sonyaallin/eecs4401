#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import *


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
    csp = CSP("binary")
    # Adding variables
    variable_array = []
    for i in range(n):
        row = []
        for j in range(n):
            var = Variable("({i},{j})".format(i=i, j=j), list(range(1, n + 1)))
            row.append(var)
            csp.add_var(var)
        variable_array.append(row)

    # Adding constraints between every cell in each row and each column
    constraints = []
    for i in range(n):
        for j in range(n):
            for k in range(j + 1, n):
                # rows
                var_scope = [variable_array[i][j], variable_array[i][k]]
                c = Constraint("({i}{j},{i}{k})".format(i=i, j=j, k=k), var_scope)
                constraints.append(c)

                # columns
                var_scope = [variable_array[j][i], variable_array[k][i]]
                c = Constraint("({j}{i},{k}{i})".format(i=i, j=j, k=k), var_scope)
                constraints.append(c)

    # Adding a permutation of all NON-EQUAL integer pairs as satisfying conditions
    tuples = list(permutations(list(range(1, n + 1)), 2))
    for c in constraints:
        c.add_satisfying_tuples(tuples)
        csp.add_constraint(c)

    return csp, variable_array


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
    csp = CSP("nary_ad")
    rows = []
    columns = [[] for i in range(n)]

    # Adding variables
    variable_array = []
    for i in range(n):
        row = []
        for j in range(n):
            var = Variable("({i},{j})".format(i=i, j=j), list(range(1, n + 1)))
            row.append(var)
            csp.add_var(var)
            columns[j].append(var)

        rows.append(row)
        variable_array.append(row)

    # Adding constraints between for each row and column using arrays made above
    constraints = []
    for i in range(n):
        # rows
        c = Constraint("Row{i}".format(i=i), rows[i])
        constraints.append(c)

        # columns
        c = Constraint("Col{i}".format(i=i), columns[i])
        constraints.append(c)

    # Adding a permutation of all NON-EQUAL integer pairs as satisfying conditions
    tuples = list(permutations(list(range(1, n + 1)), n))
    for c in constraints:
        c.add_satisfying_tuples(tuples)
        csp.add_constraint(c)

    return csp, variable_array


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
    csp, variable_array = binary_ne_grid(funpuzz_grid)
    csp.name = "funpuzz"

    for cage in range(1, len(funpuzz_grid)):
        operation = funpuzz_grid[cage][-1]
        target = funpuzz_grid[cage][-2]
        var_scope = []
        all_domain = []
        for cell in range(len(funpuzz_grid[cage]) - 2):
            i = int(str(funpuzz_grid[cage][cell])[0]) - 1
            j = int(str(funpuzz_grid[cage][cell])[1]) - 1
            all_domain.append(variable_array[i][j].domain())
            var_scope.append(variable_array[i][j])

        satisfying_tuples = []
        c = Constraint("cage{cage}".format(cage=cage), var_scope)

        # We need the cartesian product of the domains of each variable in the cage because we only want one variable
        # from each cell, then out of each possible domain, find out if the domain has the numbers that can achieve
        # the target
        catesian_product = product(*all_domain)
        for domain in catesian_product:
            if operation == 0:
                if sum(domain) == target:
                    satisfying_tuples.append(domain)
            elif operation == 1:
                if _subtraction_dom(domain, target):
                    satisfying_tuples.append(domain)
            elif operation == 2:
                if _quotient_dom(domain, target):
                    satisfying_tuples.append(domain)
            elif operation == 3:
                if _product_dom(domain, target):
                    satisfying_tuples.append(domain)

        c.add_satisfying_tuples(satisfying_tuples)
        csp.add_constraint(c)

    return csp, variable_array


def _subtraction_dom(domain, target):
    for dom in permutations(domain):
        result = dom[0]
        for n in range(1, len(dom)):
            result -= dom[n]
        if result == target:
            return True
    return None


def _quotient_dom(domain, target):
    for dom in permutations(domain):
        result = dom[0]
        for j in range(1, len(dom)):
            result /= dom[j]
        if result == target:
            return True
    return None


def _product_dom(domain, target):
    result = 1
    for i in domain:
        result *= i
    if result == target:
        return True
    return False
