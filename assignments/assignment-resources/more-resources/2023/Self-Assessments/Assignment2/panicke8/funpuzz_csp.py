# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from re import L
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
    lst_dom = []
    lst_constraints = []
    variable_array = []  # Contains Variable types
    funpuzz_csp = CSP("the_csp")
    # Populate domain w every possible row/col value
    for i in range(funpuzz_grid[0][0]):
        lst_dom.append(i + 1)

     # Populate variable array with vars dep on domain
    for row in lst_dom:
        lst_row = []
        for col in lst_dom:
            # ex. Var12 is the box in row 1 col 2
            lst_row.append(Variable("{}{}".format(row, col), lst_dom))
        for r in lst_row:
            funpuzz_csp.add_var(r)
        variable_array.append(lst_row)

     # Row + Col constraints
    for row in range(len(lst_dom)):  # for row in lst_dom:
        for col in range(len(lst_dom)):  # for col in lst_dom:
            lst_constraints.extend(helper_bin_ne(
                "R", variable_array, row, col, funpuzz_csp))
            lst_constraints.extend(helper_bin_ne(
                "C", variable_array, row, col, funpuzz_csp))
    return funpuzz_csp, variable_array


def helper_bin_ne(constraint, variable_array, row, col, funpuzz_csp):
    lst_constraints = []  # Contains binary constraints only
    tup_satisfied = []  # Contains tuples that satify the constraints
    # Iterating over all of the rows

    for v in range(len(variable_array[row])):
        if (constraint == "C"):  # If there's a column constraint
            if (v <= row):
                continue
            v1 = variable_array[row][col]
            v2 = variable_array[v][col]
            # Add curr constraint to csp
            constraint_to_add = Constraint("Cons(Var{}{}, Var{}{})".format(
                row + 1, col + 1, v + 1, col + 1), [v1, v2])
            funpuzz_csp.add_constraint(constraint_to_add)

        else:  # If there's a row constraint
            if (v <= col):
                continue
            v1 = variable_array[row][col]
            v2 = variable_array[row][v]
            # Add curr constraint to csp
            constraint_to_add = Constraint("Cons(Var{}{}, Var{}{})".format(
                row + 1, col + 1, row + 1, v + 1), [v1, v2])
            funpuzz_csp.add_constraint(constraint_to_add)

        for a in v1.domain():
            for b in v2.domain():
                if a != b:
                    tup_satisfied.append((a, b))

        # Will return a list of constraints back to main function
        constraint_to_add.add_satisfying_tuples(tup_satisfied)
        lst_constraints.append(constraint_to_add)
    return lst_constraints


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
    pass


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
    # Using binary not-equal constraints
    funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)

    # Adding cage constraints
    for cage in range(1, len(funpuzz_grid)):
        # There are 2 elements, so first one is a cell variable and second one is the value needed in that cell
        if (len(funpuzz_grid[cage]) <= 2):
            first = int(str(funpuzz_grid[cage][0])[0]) - 1
            second = int(str(funpuzz_grid[cage][0])[1]) - 1

            domain = funpuzz_grid[cage][1]
            variable_array[first][second] = Variable(
                "{}{}".format(first, second), [domain])
            funpuzz_csp.add_var(variable_array[first][second])
        else:
            lst_cage_doms = []
            lst_cage_vars = []
            # Last two elements of funpuzz_grid[cage] are the target number, and the operator
            num_needed = funpuzz_grid[cage][-2]
            op = funpuzz_grid[cage][-1]
            #print("op = ", op)
            # print("num_needed",num_needed)

            for box in range(len(funpuzz_grid[cage]) - 2):
                first = int(str(funpuzz_grid[cage][box])[0]) - 1
                second = int(str(funpuzz_grid[cage][box])[1]) - 1
                # Populating cage domains based on the variables
                lst_cage_doms.append(variable_array[first][second].domain())
                # Populating cage variables themselves
                lst_cage_vars.append(variable_array[first][second])

                tup_satisfied = []  # Contains tuples that satisfy the constraints
                constraint_to_add = Constraint(
                    "Cons(Cg{})".format(cage), lst_cage_vars)

                # Use itertools' product() method to take the Cartiesian product btwn the cage domains
                for curr_dom in itertools.product(*lst_cage_doms):
                    perms = itertools.permutations(curr_dom)
                    # Call the helper to perform the appropirate operation and return a tuple
                    tup_satisfied = helper_op_constraints(
                        op, curr_dom, tup_satisfied, perms, num_needed)

            #print("satisfied tuples: ", tup_satisfied)
            constraint_to_add.add_satisfying_tuples(tup_satisfied)
            #print("cage constraint: ", constraint_to_add)
            funpuzz_csp.add_constraint(constraint_to_add)
    return funpuzz_csp, variable_array


def helper_op_constraints(op, curr_dom, tup_satisfied, perms, num_needed):
    # ADDITION
    if op == 0:
        final = 0
        for n in curr_dom:
            final += n
        if num_needed == final:
            tup_satisfied.append(curr_dom)
    # MULTIPLICATION
    if op == 3:
        final = 1
        for n in curr_dom:
            final *= n
        if num_needed == final:
            tup_satisfied.append(curr_dom)

    # Use itertools' permutations() method to generate all possible orderings without repeated elements
    # SUBTRACTION
    if op == 1:
        for n in perms:
            final = n[0]
            for k in range(1, len(n)):
                final -= n[k]
            if num_needed == final:
                tup_satisfied.append(curr_dom)
    # DIVISION
    if op == 2:
        for n in perms:
            final = n[0]
            for k in range(1, len(n)):
                final /= n[k]
            if num_needed == final:
                tup_satisfied.append(curr_dom)
    return tup_satisfied
