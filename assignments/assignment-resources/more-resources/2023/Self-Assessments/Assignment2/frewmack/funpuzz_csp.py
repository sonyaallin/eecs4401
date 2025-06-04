#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''
from itertools import permutations, product, accumulate
from cspbase import *

ADD = 0
SUBTRACT = 1
DIVIDE = 2
MULTIPLY = 3

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
    N = funpuzz_grid[0][0]
    vars = [[Variable(f"[{i}][{j}]", domain=[(n + 1) for n in range(N)]) for j in range(N)] for i in range(N)]
    csp = CSP(
        "binary_ne_grid", 
    )
    for var_list in vars:
        for var in var_list:
            csp.add_var(var)

    binary_nequal_tuples = [(x+1, y+1) for x in range(N) for y in range(N) if y != x]

    positions = [(i, j) for i in range(N) for j in range(N)]

    for i_1, j_1 in positions:
        # row
        for j_2 in range(j_1+1, N):
            con = Constraint(f"[{i_1}][{j_1}]!=[{i_1}][{j_2}]", [vars[i_1][j_1], vars[i_1][j_2]])
            con.add_satisfying_tuples(binary_nequal_tuples)
            csp.add_constraint(con)

        # column
        for i_2 in range(i_1+1, N):
            con = Constraint(f"[{i_1}][{j_1}]!=[{i_2}][{j_1}]", [vars[i_1][j_1], vars[i_2][j_1]])
            con.add_satisfying_tuples(binary_nequal_tuples)
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
    N = funpuzz_grid[0][0]
    vars = [[Variable(f"[{i}][{j}]", domain=[(n + 1) for n in range(N)]) for j in range(N)] for i in range(N)]
    csp = CSP(
        "nary_ad_grid", 
    )
    for var_list in vars:
        for var in var_list:
            csp.add_var(var)

    nary_all_diff_tuples = [*permutations(range(1, N+1), N)]

    for i in range(N):
        row_scope = []
        col_scope = []
        for j in range(N):
            row_scope.append(vars[i][j])
            col_scope.append(vars[j][i])
        row_con = Constraint(f"[{i}][...]alldiff", row_scope)
        row_con.add_satisfying_tuples(nary_all_diff_tuples)
        csp.add_constraint(row_con)
        col_con = Constraint(f"[...][{i}]alldiff", col_scope)
        col_con.add_satisfying_tuples(nary_all_diff_tuples)
        csp.add_constraint(col_con)

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
    # Opt for binary constraints, since it doesn't generate N! tuples like all-diff
    csp, vars = binary_ne_grid(funpuzz_grid)
    csp.name = "funpuzz_csp_model"
    N = funpuzz_grid[0][0]

    for cage in funpuzz_grid[1:]:
        if len(cage) == 2:
            x, y = ((cage[0] // 10) - 1, (cage[0] % 10) - 1)
            target = cage[1]
            con = Constraint(f"[{x}][{y}]=={target}", scope=[vars[x][y]])
            con.add_satisfying_tuples((target,))
            csp.add_constraint(con)
            continue

        cells = [*map(lambda x: ((x // 10) - 1, (x % 10) - 1), cage[:-2])]
        target = cage[-2]
        operation = cage[-1]

        scope = [vars[i][j] for (i, j) in cells]
        con = Constraint(str(cage), scope)

        # generate every combination of values including repeats
        # (the other constraints handle all-diff for us)
        arrangements = [*product(range(1, N+1), repeat=len(cells))]
        sat_tuples = []
        op = None
        if operation == ADD:
            op = lambda x, y: x+y
        elif operation == SUBTRACT:
            op = lambda x, y: x-y
        elif operation == DIVIDE:
            op = lambda x, y: x/y
        elif operation == MULTIPLY:
            op = lambda x, y: x*y

        for a in arrangements:
            if operation == ADD or operation == MULTIPLY:
                # operations are commutative
                if [*accumulate(a, op)][-1] == target:
                    sat_tuples.append(a)
            else:
                # operations are non-commutative; check every permutation
                perms = permutations(a)
                arrangement_works = False
                for perm in perms:
                    try:
                        if [*accumulate(perm, op)][-1] == target:
                            arrangement_works = True
                            break
                    except ZeroDivisionError:
                        continue
                if arrangement_works:
                    sat_tuples.append(a)

        con.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(con)

    return csp, vars


