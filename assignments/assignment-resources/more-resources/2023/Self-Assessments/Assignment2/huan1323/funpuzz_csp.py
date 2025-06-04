#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

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
    l, variable_array, funpuzz_csp = funpuzz_grid[0][0], [], CSP("Binary grid")
    for i in range(1, l+1):
        sub_vars = []
        for j in range(1, l+1):
            var = Variable(str(i)+str(j), [x for x in range(1, l+1)])
            sub_vars.append(var)
            funpuzz_csp.add_var(var)
        variable_array.append(sub_vars)

    satisfy = []
    for x in range(1, l+1):
        for y in range(1, l+1):
            if x != y:
                satisfy.append([x, y])

    for row in range(l):
        for col in range(l):
            x = 1
            while col+x < l:
                con = Constraint(variable_array[row][col].name + " " +
                                 variable_array[row][col+x].name,
                                 [variable_array[row][col],
                                  variable_array[row][col+x]])
                con.add_satisfying_tuples(satisfy)
                funpuzz_csp.add_constraint(con)
                x += 1
    for col in range(l):
        for row in range(l):
            x = 1
            while row+x < l:
                con = Constraint(variable_array[row][col].name + " " +
                                 variable_array[row+x][col].name,
                                 [variable_array[row][col],
                                  variable_array[row+x][col]])
                con.add_satisfying_tuples(satisfy)
                funpuzz_csp.add_constraint(con)
                x += 1
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
    l, variable_array, funpuzz_csp = funpuzz_grid[0][0], [], CSP("nary grid")
    for i in range(1, l+1):
        sub_vars = []
        for j in range(1, l+1):
            var = Variable(str(i)+str(j), [x for x in range(1, l+1)])
            sub_vars.append(var)
            funpuzz_csp.add_var(var)
        variable_array.append(sub_vars)

    satisfy = []
    for sub_sat in all_diff(l):
        satisfy.append(tuple(sub_sat))
    for row in range(l):
        con = Constraint("row"+str(row+1), [x for x in variable_array[row]])
        con.add_satisfying_tuples(satisfy)
        funpuzz_csp.add_constraint(con)
    for col in range(l):
        vars = []
        for i in range(l):
            vars.append(variable_array[i][col])
        con = Constraint("col"+str(col+1), vars)
        con.add_satisfying_tuples(satisfy)
        funpuzz_csp.add_constraint(con)
    return funpuzz_csp, variable_array


def all_diff(n):
    if n == 2:
        satisfy = []
        for x in range(1, n+1):
            for y in range(1, n+1):
                if x != y:
                    satisfy.append([x, y])
        return satisfy

    sat = []
    satisfy = all_diff(n-1)
    for sub_sat in satisfy:
        for j in range(len(sub_sat)+1):
            s = sub_sat.copy()
            s.insert(j, n)
            sat.append(s)
    return sat



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
    funpuzz_csp, vars = binary_ne_grid(funpuzz_grid)
    # funpuzz_csp, vars = nary_ad_grid(funpuzz_grid)
    for rule in range(1, len(funpuzz_grid)):
        scope = []
        for cell in funpuzz_grid[rule][:-2]:
            i , j = cell % 10, cell // 10
            scope.append(vars[i-1][j-1])
        con = Constraint("cage"+str(rule), scope)
        con.add_satisfying_tuples(get_all_sat(funpuzz_grid[0][0], len(funpuzz_grid[rule])-2, funpuzz_grid[rule][-1], funpuzz_grid[rule][-2]))
        funpuzz_csp.add_constraint(con)
    return funpuzz_csp, vars


def get_all_conditions(r, n):
    acc = []
    for x in range(1, r+1):
        acc.append([x])
    return get_all_conditions_helper(r, n-1, acc)


def get_all_conditions_helper(r, n, acc):
    if n == 0:
        return acc
    result = []
    for cond in acc:
        for i in range(1, r+1):
            result.append(cond+[i])
    return get_all_conditions_helper(r, n-1, result)


def get_all_sat(r, n, operation, goal):
    result = []
    conds = get_all_conditions(r, n)
    for cond in conds:
        if operation == 0:
            if check_plus(cond, goal):
                result.append(tuple(cond))
        if operation == 3:
            if check_times(cond, goal):
                result.append(tuple(cond))
        if operation == 1:
            if check_minus(cond, goal):
                result.append(tuple(cond))
        if operation == 2:
            if check_divides(cond, goal):
                result.append(tuple(cond))
    return result


def check_plus(cond, goal):
    result = 0
    for i in cond:
        result += i
    return result == goal


def check_times(cond, goal):
    result = 1
    for i in cond:
        result *= i
    return result == goal


def check_minus(cond, goal):
    for i in range(len(cond)):
        if check_minus_helper(cond[:i]+cond[i+1:], goal, cond[i]):
            return True
    return False


def check_minus_helper(cond, goal, acc):
    if cond == []:
        return acc == goal
    for i in range(len(cond)):
        if check_minus_helper(cond[:i]+cond[i+1:], goal, acc-cond[i]):
            return True
    return False


def check_divides(cond, goal):
    for i in range(len(cond)):
        if check_divides_helper(cond[:i]+cond[i+1:], goal, cond[i]):
            return True
    return False


def check_divides_helper(cond, goal, acc):
    if cond == []:
        return acc == goal
    for i in range(len(cond)):
        if check_divides_helper(cond[:i]+cond[i+1:], goal, acc/cond[i]):
            return True
    return False
