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
    variables = []
    size = funpuzz_grid[0][0]
    for row in range(1, size + 1):
        for col in range(1, size + 1):
            var_num = str(row) + str(col)
            variables.append(Variable(var_num, [*range(1, size + 1, 1)]))
    csp = CSP("binary_ne_grid", variables)
    combos = list(itertools.permutations(range(1, size + 1), 2))
    # add constraints to csp
    for var in variables:
        for v in variables:
            var_l = []
            if v != var:
                if v.name[0] == var.name[0]:
                    var_l.append(var)
                    var_l.append(v)
                    constraint = Constraint("BIN for Row " + str(var.name[0]),
                                            var_l)
                    constraint.add_satisfying_tuples(combos)
                    csp.add_constraint(constraint)
                elif v.name[1] == var.name[1]:
                    var_l.append(var)
                    var_l.append(v)
                    constraint = Constraint("BIN for Col " + str(var.name[1]),
                                            var_l)
                    constraint.add_satisfying_tuples(combos)
                    csp.add_constraint(constraint)

    i = 0
    matrix = []
    for x in range(size):
        l = []
        for y in range(size):
            l.append(variables[i])
            i += 1
        matrix.append(l)

    return csp, matrix


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
    variables = []
    size = funpuzz_grid[0][0]
    for row in range(1, size + 1):
        for col in range(1, size + 1):
            var_num = str(row) + str(col)
            variables.append(Variable(var_num, [*range(1, size + 1, 1)]))
    csp = CSP("nary_ad_grid", variables)
    combos = list(itertools.permutations(range(1, size + 1), size))
    for var in variables:
        var_r = [var]
        var_c = [var]
        for v in variables:
            if v != var:
                if v.name[0] == var.name[0]:
                    var_r.append(v)
                elif v.name[1] == var.name[1]:
                    var_c.append(v)
        # row constraints
        constraint = Constraint("All Dif for Row " + str(var.name[0]),
                                var_r)
        constraint.add_satisfying_tuples(combos)
        csp.add_constraint(constraint)
        # col constraints
        constraint = Constraint("All Dif for Col " + str(var.name[1]),
                                var_c)
        constraint.add_satisfying_tuples(combos)
        csp.add_constraint(constraint)
    i = 0
    matrix = []
    for x in range(size):
        l = []
        for y in range(size):
            l.append(variables[i])
            i += 1
        matrix.append(l)

    return csp, matrix


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
    variables = []
    matrix = []
    size = funpuzz_grid[0][0]

    for row in range(1, size + 1):
        for col in range(1, size + 1):
            var_num = str(row) + str(col)
            variables.append(Variable(var_num, [*range(1, size + 1, 1)]))
    csp = CSP("funpuzz_grid", variables)
    combos = list(itertools.permutations(range(1, size + 1), 2))
    # add constraints to csp
    for var in variables:
        for v in variables:
            var_l = []
            if v != var:
                if v.name[0] == var.name[0]:
                    var_l.append(var)
                    var_l.append(v)
                    constraint = Constraint("All Dif for Row " + str(var.name[0]),
                                            var_l)
                    constraint.add_satisfying_tuples(combos)
                    csp.add_constraint(constraint)
                elif v.name[1] == var.name[1]:
                    var_l.append(var)
                    var_l.append(v)
                    constraint = Constraint("All Dif for Col " + str(var.name[1]),
                                            var_l)
                    constraint.add_satisfying_tuples(combos)
                    csp.add_constraint(constraint)
    # (0=’+’, 1=’-’, 2=’/’, 3=’*’)
    for x in range(1, len(funpuzz_grid)):

        vars = funpuzz_grid[x][:-2]
        f_var = []
        for v in variables:
            for v1 in vars:
                if v.name == str(v1):
                    f_var.append(v)
                    break
        target = funpuzz_grid[x][-2]
        op = funpuzz_grid[x][-1]
        same_rows = []
        same_cols = []
        combs = list(itertools.permutations(range(1, size + 1),len(f_var)))
        combs2 = list(itertools.combinations_with_replacement(range(1, size + 1),len(f_var)))
        for t in combs2:
            t2 = itertools.permutations(list(t),len(t))
            for y in t2:
                combs.append(y)
        perms = []
        for tup in combs:
            a0 = list(tup)
            a = list(itertools.permutations(a0, len(a0)))
            for pos_tup in a:
                if pos_tup not in perms:
                    perms.append(pos_tup)

        # plus
        tups = []
        if op == 0:
            for c in perms:
                if check(list(c),vars):
                    sum = 0
                    for x in c:
                        sum += x
                    if sum == target:
                        tups.append(c)
        # minus
        elif op == 1:
            for c in perms:
                if check(list(c),vars):
                    sum = float('inf')
                    for x in c:
                        if sum == float('inf'):
                            sum = x
                        else:
                            sum -= x
                    if sum == target:
                        tups.append(c)
        # divide
        elif op == 2:
            for c in perms:
                if check(list(c),vars):
                    sum = float('inf')
                    for x in c:
                        if sum == float('inf'):
                            sum = x
                        else:
                            sum = sum / x
                    if sum == target:
                        tups.append(c)
        # multiply
        elif op == 3:
            for c in perms:
                if check(list(c),vars):
                    sum = 1
                    for x in c:
                        sum = sum * x
                    if sum == target:
                        tups.append(c)
        p2 = []
        for t in tups:
            a0 = list(t)
            a = itertools.permutations(a0,len(t))
            for x in a:
                if check(list(x),vars):
                    p2.append(x)


        constraint = Constraint("cage cons", f_var)
        constraint.add_satisfying_tuples(p2)
        csp.add_constraint(constraint)

    i = 0
    for x in range(size):
        l = []
        for y in range(size):
            l.append(variables[i])
            i += 1
        matrix.append(l)

    return csp, matrix


def check(lst, vars):
    i = 0
    for v in vars:
        val = lst[i]
        j = 0
        for v2 in vars:
            if v != v2:
                if str(v)[0] == str(v2)[0]:
                    # checks if values are different
                    if val == lst[vars.index(v2)]:
                        return False
                if str(v)[1] == str(v2)[1]:
                    # checks if values are different
                    if val == lst[vars.index(v2)]:
                        return False
                j += 1
        i += 1

    return True
