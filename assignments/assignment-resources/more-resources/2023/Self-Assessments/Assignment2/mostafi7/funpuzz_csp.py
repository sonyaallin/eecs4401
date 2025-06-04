# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from re import X
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
    variable_array = variables_list(n)
    constraints = []
    satisfying = list(itertools.permutations(list(range(1, n+1)), 2))

    for r in range(n):
        for c in range(n):
            v1 = variable_array[r][c]
            for x in range(c+1, n):
                v2 = variable_array[r][x]
                con = Constraint("Cons(V{}{}, V{}{})".format(
                    r+1, c+1, r+1, x+1), [v1, v2])
                con.add_satisfying_tuples(satisfying)
                constraints.append(con)
            for y in range(r+1, n):
                v2 = variable_array[y][c]
                con = Constraint("Cons(V{}{}, V{}{})".format(
                    r+1, c+1, y+1, c+1), [v1, v2])
                con.add_satisfying_tuples(satisfying)
                constraints.append(con)

    variables = []
    for row in variable_array:
        for var in row:
            variables.append(var)

    funpuzz_csp = CSP("binary_ne_grid", variables)

    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array


def variables_list(n):
    variable_array = [[0 for i in range(n)] for j in range(n)]
    for r in range(n):
        for c in range(n):
            variable_array[r][c] = Variable(
                "V{}{}".format(r+1, c+1), list(range(1, n+1)))
    return variable_array


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
    variable_array = variables_list(n)
    constraints = nary_constraints(n, variable_array)

    variables = []
    for row in variable_array:
        for var in row:
            variables.append(var)

    funpuzz_csp = CSP("nary_ad_grid", variables)

    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array


def nary_constraints(n, variable_array):
    constraints = []
    satisfying = list(itertools.permutations(list(range(1, n+1)), n))

    for i in range(n):
        row_cons = Constraint("Cons(Row{})".format(i+1), variable_array[i])
        col_cons = Constraint("Cons(Col{})".format(i+1), [variable_array[x][i] for x in range(n)])
        row_cons.add_satisfying_tuples(satisfying)
        col_cons.add_satisfying_tuples(satisfying)
        constraints.append(row_cons)
        constraints.append(col_cons)
    
    return constraints


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
    variable_array = variables_list(n)
    constraints = nary_constraints(n, variable_array)

    for i, l in enumerate(funpuzz_grid[1:]):
       cons_variables = []
       satisfying = []

       for v in l[:-2]:
          cons_variables.append(variable_array[((v//10)%10)-1][(v%10)-1])
       
       cons = Constraint("Cons(Cage{})".format(i+1), cons_variables)
       if l[-1] == 0:
          for x in list(itertools.combinations_with_replacement(list(range(1, n+1)), len(l)-2)):
             if sum(x) == l[-2]:
                satisfying.extend(list(itertools.permutations(x)))
       elif l[-1] == 1: #TODO fix
          for x in list(itertools.product(list(range(1, n+1)), repeat=len(l)-2)):
             diff = x[0]
             for y in x[1:]:
                diff -= y
             if diff == l[-2]:
                satisfying.extend(list(itertools.permutations(x)))
       elif l[-1] == 2:
          for x in list(itertools.product(list(range(1, n+1)), repeat=len(l)-2)):
             div = x[0]
             for y in x[1:]:
                div /= y
             if div == l[-2]:
                satisfying.extend(list(itertools.permutations(x)))
       elif l[-1] == 3:
          for x in list(itertools.combinations_with_replacement(list(range(1, n+1)), len(l)-2)):
             prod = x[0]
             for y in x[1:]:
                prod *= y
             if prod == l[-2]:
                satisfying.extend(list(itertools.permutations(x)))
       cons.add_satisfying_tuples(satisfying)
       constraints.append(cons)
      
    variables = []
    for row in variable_array:
        for var in row:
            variables.append(var)

    funpuzz_csp = CSP("funpuzz_csp_model", variables)

    for cons in constraints:
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array
