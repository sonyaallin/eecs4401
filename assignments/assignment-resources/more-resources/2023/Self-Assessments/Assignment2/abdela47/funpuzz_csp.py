# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''
import itertools
import math

from cspbase import *


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
    csp = CSP("Binary NE CSP")
    v_array = []
    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]
    for i in range(n):
        curr_row = []
        for j in range(n):
            new_var = Variable(f'{i + 1}{j + 1}', domain)
            curr_row.append(new_var)
            csp.add_var(new_var)
        v_array.append(curr_row)
    combos = list(itertools.combinations(domain, 2))
    for l in range(n):
        for num in range(math.comb(n, 2)):
            j = combos[num]

            vars_in_scope_r = [v_array[l][j[0] - 1], v_array[l][j[1] - 1]]
            vars_in_scope_c = [v_array[j[0] - 1][l], v_array[j[1] - 1][l]]

            rc = Constraint(f"Row {l + 1} Constraint {num + 1}", vars_in_scope_r)
            cc = Constraint(f"Column {l + 1} Constraint {num + 1}", vars_in_scope_c)

            sat_tuples = list(itertools.permutations(domain, 2))

            rc.add_satisfying_tuples(sat_tuples)
            cc.add_satisfying_tuples(sat_tuples)

            csp.add_constraint(rc)
            csp.add_constraint(cc)

    return csp, v_array


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
    csp = CSP("N-ary AD CSP")
    v_array = []
    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]
    for i in range(n):
        curr_row = []
        for j in range(n):
            new_var = Variable(f'{i + 1}{j + 1}', domain)
            curr_row.append(new_var)
            csp.add_var(new_var)
        v_array.append(curr_row)

    sat_tuples = list(itertools.permutations(domain, n))
    for l in range(n):
        vars_in_scope_r = v_array[l]
        vars_in_scope_c = [row[l] for row in v_array]

        rc = Constraint(f"Row {l + 1} Constraint", vars_in_scope_r)
        cc = Constraint(f"Column {l + 1} Constraint", vars_in_scope_c)

        rc.add_satisfying_tuples(sat_tuples)
        cc.add_satisfying_tuples(sat_tuples)

        csp.add_constraint(rc)
        csp.add_constraint(cc)

    return csp, v_array


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
    csp, v_array = binary_ne_grid(funpuzz_grid)
    n = funpuzz_grid[0][0]
    domain = [i for i in range(1, n + 1)]
    if len(funpuzz_grid) > 1:
        index = 1
        while index < len(funpuzz_grid):
            curr_cage_constraint = funpuzz_grid[index]
            if len(curr_cage_constraint) == 2:
                cell = str(curr_cage_constraint[0])
                var = v_array[int(cell[0])-1][int(cell[1])-1]
                c = Constraint("Enforce Target", [var])
                c.add_satisfying_tuples((curr_cage_constraint[-1],))
                csp.add_constraint(c)
            else:
                num_var_in_scope = len(curr_cage_constraint) - 2
                target = curr_cage_constraint[-2]
                op = curr_cage_constraint[-1]
                vars_in_scope = []
                for i in range(num_var_in_scope):
                    var_str = str(curr_cage_constraint[i])
                    var = v_array[int(var_str[0])-1][int(var_str[1])-1]
                    vars_in_scope.append(var)
                if op == 0:
                    c = Constraint("Addition Cage Constraint", vars_in_scope)
                    sat_tups = [p for p in itertools.permutations(domain, num_var_in_scope) if sum(p) == target]
                elif op == 1:
                    c = Constraint("Subtraction Cage Constraint", vars_in_scope)
                    sat_tups = []
                    for p in itertools.permutations(domain, num_var_in_scope):
                        for op_perm in itertools.permutations(p):
                            s = op_perm[0]
                            for num in op_perm[1:]:
                                s -= num
                            if s == target:
                                sat_tups.append(p)
                                break
                elif op == 2:
                    c = Constraint("Division Cage Constraint", vars_in_scope)
                    sat_tups = []
                    for p in itertools.permutations(domain, num_var_in_scope):
                        for op_perm in itertools.permutations(p):
                            s = op_perm[0]
                            for num in op_perm[1:]:
                                s /= num
                            if s == target:
                                sat_tups.append(p)
                                break
                else:
                    c = Constraint("Multiplication Cage Constraint", vars_in_scope)
                    sat_tups = [p for p in itertools.permutations(domain, num_var_in_scope) if math.prod(p) == target]
                c.add_satisfying_tuples(sat_tups)
                csp.add_constraint(c)
            index += 1

    return csp, v_array
    # raise NotImplementedError
