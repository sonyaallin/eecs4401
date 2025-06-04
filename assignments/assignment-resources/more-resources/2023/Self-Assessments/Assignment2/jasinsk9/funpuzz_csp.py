#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import numpy as np
import itertools as it

from propagators import prop_BT


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
    csp = CSP('Binary Grid')
    sat_tuples = []
    set = list(range(1, funpuzz_grid[0][0] + 1))
    for i in range(1, funpuzz_grid[0][0] + 1):
        for j in range(1, funpuzz_grid[0][0] + 1):
            name = i * 10 + j
            v = Variable(str(name), set)
            csp.add_var(v)
            if i != j and (i, j) not in sat_tuples:
                sat_tuples.append((i, j))
                sat_tuples.append((j, i))
    vars = csp.get_all_vars()
    rows = []
    cols = []
    for var1 in vars:
        for var2 in vars:
            if var1 != var2:
                if var1.name[0] == var2.name[0] and var1.name + var2.name not in rows:
                    c = Constraint((var1.name + '/' + var2.name), (var1, var2))
                    c.add_satisfying_tuples(sat_tuples)
                    csp.add_constraint(c)
                    rows.append(var2.name + var1.name)
                if var1.name[1] == var2.name[1] and var1.name + var2.name not in cols:
                    c = Constraint((var1.name + '/' + var2.name), (var1, var2))
                    c.add_satisfying_tuples(sat_tuples)
                    csp.add_constraint(c)
                    cols.append(var2.name + var1.name)
    vars = np.array(vars)
    vars = vars.reshape(funpuzz_grid[0][0], funpuzz_grid[0][0])
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
    csp = CSP('N-ary Grid')
    set = list(range(1, funpuzz_grid[0][0] + 1))
    for i in range(1, funpuzz_grid[0][0] + 1):
        for j in range(1, funpuzz_grid[0][0] + 1):
            name = i * 10 + j
            v = Variable(str(name), set)
            csp.add_var(v)
    vars = csp.get_all_vars()
    vars = np.array(vars)
    vars = vars.reshape(funpuzz_grid[0][0], funpuzz_grid[0][0])
    sat_tuples = list(it.permutations(list(range(1, funpuzz_grid[0][0] + 1)), funpuzz_grid[0][0]))
    for row in vars:
        scope = []
        for var in row:
            scope.append(var)
        c = Constraint('Row ' + str(row[0].name[0]), scope)
        c.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(c)
    for col in vars.transpose():
        scope = []
        for var in col:
            scope.append(var)
        c = Constraint('Col' + str(col[0].name[0]), scope)
        c.add_satisfying_tuples(sat_tuples)
        csp.add_constraint(c)
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
    csp, vars = nary_ad_grid(funpuzz_grid)
    for cage in funpuzz_grid:
        if len(cage) > 3:
            symbol = cage[-1]
            target = cage[-2]
            variables = []
            for k in range(0, len(cage) - 2):
                i = cage[k] // 10
                j = cage[k] % 10
                variables.append(vars[i-1][j-1])
            c = Constraint('Cage' + str(funpuzz_grid.index(cage)), variables)
            sat_tuples = []
            if symbol == 0:
                possible = list(it.product(list(range(1, funpuzz_grid[0][0] + 1)), repeat=len(c.get_scope())))
                for tuple in possible:
                    if sum(list(tuple)) == target:
                        sat_tuples.append(tuple)
            if symbol == 1:
                possible = list(it.product(list(range(1, funpuzz_grid[0][0] + 1)), repeat=len(c.get_scope())))
                for tuple in possible:
                    value = tuple[0]
                    for i in range(1, len(tuple)):
                        value -= tuple[i]
                    if value == target:
                        sat_tuples = sat_tuples + list(it.permutations(list(tuple)))
            if symbol == 2:
                possible = list(it.product(list(range(1, funpuzz_grid[0][0] + 1)), repeat=len(c.get_scope())))
                for tuple in possible:
                    value = tuple[0]
                    for i in range(1, len(tuple)):
                        value /= tuple[i]
                    if value == target:
                        sat_tuples = sat_tuples + list(it.permutations(list(tuple)))
            if symbol == 3:
                possible = list(it.product(list(range(1, funpuzz_grid[0][0] + 1)), repeat=len(c.get_scope())))
                for tuple in possible:
                    if np.prod(list(tuple)) == target:
                        sat_tuples.append(tuple)
            c.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(c)
    return csp, vars

if __name__ == '__main__':
    boards = [[3], [11, 21, 3, 0], [12, 22, 2, 1], [13, 23, 33, 6, 3], [31, 32, 5, 0]]
    print("binary")
    puzz, yuh = binary_ne_grid(boards)
    print("nary")
    puzz2, yuh2 = nary_ad_grid(boards)
    print("cage")
    puzz3, yuh3 = funpuzz_csp_model(boards)
    solver = BT(puzz3)
    solver.bt_search(prop_BT)

