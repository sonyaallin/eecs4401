#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''
import itertools

from cspbase import *

from itertools import permutations

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
    funpuzz_csp = CSP(name='funpuzz_csp')
    grid_size = funpuzz_grid[0][0]
    dom = []
    for i in range(1, grid_size + 1):
        dom.append(i)

    variable_array = []

    all_dif_tups = []
    for n in dom:
        for m in dom:
            if n != m:
                all_dif_tups.append((n,m))

    for i in range(1, grid_size + 1):
        variable_array.append([])
        for j in range(1, grid_size + 1):
            name = str(i) + str(j)
            var = Variable(name, dom)
            funpuzz_csp.add_var(var)
            variable_array[i - 1].append(var)

    for i in range(1, grid_size + 1):
        for j in range(1, grid_size):
            for k in range(j + 1, grid_size + 1):
                var1_n = 'r' + str(i) + str(j)
                var2_n = str(i) + str(k)
                name = var1_n + var2_n
                c = Constraint(name = name, scope=[variable_array[i - 1][j - 1], variable_array[i - 1][k - 1]])
                c.add_satisfying_tuples(list(all_dif_tups))
                funpuzz_csp.add_constraint(c)

    #columns now
    for j in range(1, grid_size + 1):
        for i in range(1, grid_size):
            for k in range(i + 1, grid_size + 1):
                var1_n = 'c' + str(i) + str(j)
                var2_n = str(k) + str(j)
                name = var1_n + var2_n
                c = Constraint(name = name, scope=[variable_array[i - 1][j - 1], variable_array[k - 1][j - 1]])
                c.add_satisfying_tuples(list(all_dif_tups))
                funpuzz_csp.add_constraint(c)
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
    funpuzz_csp = CSP(name='funpuzz_csp')
    grid_size = funpuzz_grid[0][0]
    dom = []
    for i in range(1, grid_size + 1):
        dom.append(i)

    variable_array = []

    all_dif_tups = list(itertools.permutations(dom))

    for i in range(1, grid_size + 1):
        variable_array.append([])
        for j in range(1, grid_size + 1):
            name = str(i) + str(j)
            var = Variable(name, dom)
            funpuzz_csp.add_var(var)
            variable_array[i - 1].append(var)

    for i in range(1, grid_size + 1):

        var1_n = "r" + str(i)
        name = var1_n

        scope = []
        for j in range(1, grid_size + 1):
            scope.append(variable_array[i - 1][j - 1])

        c = Constraint(name=name, scope=scope)
        c.add_satisfying_tuples(all_dif_tups)
        funpuzz_csp.add_constraint(c)

    # columns now
    for j in range(1, grid_size + 1):

        var1_n = "c" + str(j)
        name = var1_n

        scope = []
        for i in range(1, grid_size + 1):
            scope.append(variable_array[i - 1][j - 1])

        c = Constraint(name=name, scope=scope)
        c.add_satisfying_tuples(all_dif_tups)
        funpuzz_csp.add_constraint(c)


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

    add_dict = {}
    sub_dict = {}
    mul_dict = {}
    div_dict = {}

    funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)

    for item in funpuzz_grid[1:]:
        if len(item) == 2:
            var = str(item[0])
            name = 'p' + var
            val = item[1]
            i = int(var[0]) - 1
            j = int(var[1]) - 1
            c = Constraint(name=name, scope=[variable_array[i][j]])
            c.add_satisfying_tuples((val))
            funpuzz_csp.add_constraint(c)
        else:
            op = item[-1]
            target = item[-2]
            vars = item[:-2]
            scope = []
            name = 'cage' + str(target) + ':' + str(op)

            for var in vars:
                str_var = str(var)
                i = int(str_var[0]) - 1
                j = int(str_var[1]) - 1
                scope.append(variable_array[i][j])

            c = Constraint(name=name, scope=scope)

            if op < 0 or op > 4:
                raise ValueError('Operation is invalid')
            n_vars = len(vars)
            dom_list = []
            for v in scope:
                dom_list.append(v.domain())
            if op == 0:
                if (n_vars, target) not in add_dict:
                    add_dict[(n_vars, target)] = gen_addition_perms(dom_list, target)
                c.add_satisfying_tuples(list(add_dict[(n_vars, target)]))
            elif op == 1:
                if (n_vars, target) not in sub_dict:
                    sub_dict[(n_vars, target)] = gen_subtraction_perms(dom_list, target)
                c.add_satisfying_tuples(list(sub_dict[(n_vars, target)]))
            elif op == 2:
                if (n_vars, target) not in div_dict:
                    div_dict[(n_vars, target)] = gen_division_perms(dom_list, target)
                c.add_satisfying_tuples(list(div_dict[(n_vars, target)]))
            else:
                if (n_vars, target) not in mul_dict:
                    mul_dict[(n_vars, target)] = gen_multiplication_perms(dom_list, target)
                c.add_satisfying_tuples(list(mul_dict[(n_vars, target)]))
            funpuzz_csp.add_constraint(c)
    return funpuzz_csp, variable_array


def gen_addition_perms(dom_list, target):
    sat_lst = []
    perms = rec_helper(dom_list)
    for p in perms:
        if sum(p) == target:
            sat_lst.append(p)
    return sat_lst

def gen_subtraction_perms(dom_list, target):
    sat_lst = []
    perms = rec_helper(dom_list)
    for p in perms:
        i = 0
        sat_flag = False
        while i < len(p) and not sat_flag:
            if p[i] - (sum(p) - p[i]) == target:
                sat_lst.append(p)
                sat_flag = True
            i += 1
    return sat_lst

def gen_multiplication_perms(dom_list, target):
    sat_lst = []
    perms = rec_helper(dom_list)
    for p in perms:
        if lst_prod(p) == target:
            sat_lst.append(p)
    return sat_lst

def gen_division_perms(dom_list, target):
    sat_lst = []
    perms = rec_helper(dom_list)
    for p in perms:
        i = 0
        sat_flag = False
        while i < len(p) and not sat_flag:
            if p[i] / (lst_prod(p) / p[i]) == target:
                sat_lst.append(p)
                sat_flag = True
            i += 1
    return sat_lst

def rec_helper(dom_list):
    perm_list = []
    if len(dom_list) > 1:
        rest = rec_helper(dom_list[1:])
        for i in dom_list[0]:
            perm = []
            perm.append(i)
            for r in rest:
                whole_p = perm + r
                perm_list.append(whole_p)
    else:
        for i in dom_list[0]:
            perm = []
            perm.append(i)
            perm_list.append(perm)

    return perm_list

def lst_prod(lst):
    product = 1
    for i in lst:
        product *= i
    return product
