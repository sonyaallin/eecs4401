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
    return_csp = CSP('funpuzz_binary')
    dim = funpuzz_grid[0][0]  # dimension of board
    domain = []
    for num in range(1, dim + 1):  # var's domain is {1~n}
        domain.append(num)
    vars = []
    for r in range(dim):  # init variables
        row = []
        for c in range(dim):
            var = Variable('{}{}'.format(r + 1, c + 1), domain)
            row.append(var)  # give the variable name of its index
            return_csp.add_var(var)
        vars.append(row)
    constraints = []
    # row constraints
    for row in range(dim):
        for col in range(dim):
            for i in range(col + 1, dim):
                var_org = vars[row][col]
                var_cur = vars[row][i]
                c = Constraint('Row-{}{}, {}{}'.format(row + 1, col + 1, row + 1, i + 1), [var_org, var_cur])
                satisfied = []
                org_domain = var_org.domain()
                cur_domain = var_cur.domain()
                for v1 in org_domain:
                    for v2 in cur_domain:
                        if v1 != v2:
                            satisfied.append((v1, v2))
                c.add_satisfying_tuples(satisfied)
                constraints.append(c)
    # col constraints
    for row in range(dim):
        for col in range(dim):
            for i in range(row + 1, dim):
                var_org = vars[row][col]
                var_cur = vars[i][col]
                c = Constraint('Col-{}{}, {}{}'.format(row + 1, col + 1, i + 1, col + 1), [var_org, var_cur])
                satisfied = []
                org_domain = var_org.domain()
                cur_domain = var_cur.domain()
                for v1 in org_domain:
                    for v2 in cur_domain:
                        if v1 != v2:
                            satisfied.append((v1, v2))
                c.add_satisfying_tuples(satisfied)
                constraints.append(c)
    for c in constraints:
        return_csp.add_constraint(c)
    return return_csp, vars


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
    return_csp = CSP('funpuzz_nary')
    dim = funpuzz_grid[0][0]  # dimension of board
    domain = []
    for num in range(1, dim + 1):  # var's init domain is 1-n
        domain.append(num)
    vars = []
    for r in range(dim):  # init variables
        row = []
        for c in range(dim):
            var = Variable('{}{}'.format(r + 1, c + 1), domain)
            row.append(var)  # give the variable name of its index
            return_csp.add_var(var)
        vars.append(row)
    constraints = []
    # row constraints
    for row in range(dim):
        scope = vars[row]
        c = Constraint("nary_row{}".format(row + 1), scope)
        var1 = scope[0]
        satisfied = []
        var1_domain = var1.domain()
        for sat_tuple in itertools.permutations(var1_domain):
            satisfied.append(sat_tuple)
        c.add_satisfying_tuples(satisfied)
        constraints.append(c)
    # col constraints
    for col in range(dim):
        scope = []
        for row in range(dim):
            scope.append(vars[row][col])
        c = Constraint("nary_col{}".format(col + 1), scope)
        var1 = scope[0]
        satisfied = []
        var1_domain = var1.domain()
        for sat_tuple in itertools.permutations(var1_domain):
            satisfied.append(sat_tuple)
        c.add_satisfying_tuples(satisfied)
        constraints.append(c)
    for c in constraints:
        return_csp.add_constraint(c)
    return return_csp, vars


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
    return_csp, vars = binary_ne_grid(funpuzz_grid)
    return_csp.name = "funpuzz_model"
    ic = 1
    constraints = []
    while ic < len(funpuzz_grid):
        cage = funpuzz_grid[ic]
        if len(cage) >= 2:  # need to have at least two params to satisfy the constraint
            op = cage[-1]
            target = cage[-2]
            scope = []
            for cell in cage[:-2]:
                row = int(str(cell)[0]) - 1
                col = int(str(cell)[1]) - 1
                var = vars[row][col]
                scope.append(var)
            c = Constraint('cage target {} by {}'.format(target, op), scope)
            satisfied = []
            if len(scope) > 0:
                matched, sat_values = calculate_cage_value(scope, op, target)
                if matched:
                    satisfied = sat_values
            c.add_satisfying_tuples(satisfied)
            constraints.append(c)
        ic += 1
    for c in constraints:
        return_csp.add_constraint(c)
    return return_csp, vars


def calculate_cage_value(scope, operator, target):
    """
    This helper function is to calculate whether the value that the
    particular cage could result matches the target value the cage
    expects.
    This function returns a bool value and a list of tuple values.
    If returns false, then list is empty
    """
    hist = {}
    var1 = scope[0]
    var1_domain = var1.domain()
    for v in var1_domain:
        hist[v] = [(v,)]
    i = 1
    while i < len(scope):
        new_var = scope[i]
        new_domain = new_var.domain()
        new_hist = {}
        for v in hist:
            curr_v = v
            curr_t = hist[v]
            for val in new_domain:
                if operator == 0:
                    result = curr_v + val
                    new_t = []
                    for t in curr_t:
                        new_t.append(t + (val,))
                    if result not in new_hist:
                        new_hist[result] = new_t
                    else:
                        new_hist[result].extend(new_t)
                elif operator == 1:
                    result = curr_v - val
                    new_t = []
                    for t in curr_t:
                        new_t.append(t + (val,))
                    if result not in new_hist:
                        new_hist[result] = new_t
                    else:
                        new_hist[result].extend(new_t)
                    result = val - curr_v
                    new_t = []
                    for t in curr_t:
                        new_t.append(t + (val,))
                    if result not in new_hist:
                        new_hist[result] = new_t
                    else:
                        new_hist[result].extend(new_t)
                elif operator == 2:
                    result = curr_v / val
                    new_t = []
                    for t in curr_t:
                        new_t.append(t + (val,))
                    if result not in new_hist:
                        new_hist[result] = new_t
                    else:
                        new_hist[result].extend(new_t)
                    result = val / curr_v
                    new_t = []
                    for t in curr_t:
                        new_t.append(t + (val,))
                    if result not in new_hist:
                        new_hist[result] = new_t
                    else:
                        new_hist[result].extend(new_t)
                elif operator == 3:
                    result = curr_v * val
                    new_t = []
                    for t in curr_t:
                        new_t.append(t + (val,))
                    if result not in new_hist:
                        new_hist[result] = new_t
                    else:
                        new_hist[result].extend(new_t)
        i += 1
        hist = new_hist
    for v in hist:
        if v == target:
            return True, hist[v]
    return False, []


