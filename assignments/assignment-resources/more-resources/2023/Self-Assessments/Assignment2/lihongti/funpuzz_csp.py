# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools


# Helper Function #

def combination_sum(n: int, side: int, target: int):
    """
    n: number of variables
    side: the domain of variable, should be row and col
    """
    store_lst = []
    comb_lst = list(range(1, side + 1))
    it = itertools.permutations(comb_lst, n)
    for iter in it:
        # print(iter)
        if sum(iter) == target:
            store_lst.append(iter)
    # print(store_lst)
    return store_lst


def combination_product(n: int, side: int, target: int):
    store_lst = []
    comb_lst = list(range(1, side + 1))
    it = itertools.permutations(comb_lst, n)
    for iter in it:
        # print(iter)
        prod = 1
        for num in iter:
            prod *= num
        if prod == target:
            store_lst.append(iter)
    # print(store_lst)
    return store_lst


def combination_minor(n: int, side: int, target: int):
    store_lst = []
    comb_lst = list(range(1, side + 1))
    it = itertools.permutations(comb_lst, n)
    for iter in it:
        # print(iter)
        init = iter[0]
        for index in range(1, len(iter)):
            init -= iter[index]
        if init == target:
            fi_tuples = itertools.permutations(iter, n)
            for fi in fi_tuples:
                store_lst.append(fi)
    # print(store_lst)
    return store_lst


def combination_div(n: int, side: int, target: int):
    store_lst = []
    comb_lst = list(range(1, side + 1))
    it = itertools.permutations(comb_lst, n)
    for iter in it:
        # print(iter)
        init = iter[0]
        for index in range(1, len(iter)):
            init /= iter[index]
        if init == float(target):
            fi_tuples = itertools.permutations(iter, n)
            for fi in fi_tuples:
                store_lst.append(fi)
    # print(store_lst)
    return store_lst


#
def premu(n):
    """
    return premutation of n
    """
    lst = []
    if n == 1:
        return ['1']
    else:
        rest_lst = premu(n - 1)
        for string in rest_lst:
            for i in range(n):
                str_lst = [char for char in string]
                str_lst.insert(i, str(n))
                lst.append(''.join(str_lst))
    return lst


def str_premu_tuple(l: list):
    """
    return a list of satisfied tuple for n-ary
    """
    store_lst = []
    for s in l:
        temp_tu = tuple(s)
        tu_list = []
        for s2 in temp_tu:
            tu_list.append(int(s2))
        re_tu = tuple(tu_list)
        store_lst.append(re_tu)
    return store_lst


# Main Function #


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
    # instantiate csp
    init_csp = CSP("grid_csp")
    side_length = funpuzz_grid[0][0]
    sat_tus = []
    var_lst = []

    # make a var_list for return
    for i in range(side_length):
        inner_var_lst = []
        for j in range(side_length):
            # add domain as [1 - n]
            tmp_var = Variable(("{}{}".format(i + 1, j + 1)),
                               list(range(1, side_length + 1)))
            inner_var_lst.append(tmp_var)
            init_csp.add_var(tmp_var)

            if i != j:
                sat_tus.append((i + 1, j + 1))
            # print(tmp_var.assignedValue)
            # print(tmp_var.print_all())
        var_lst.append(inner_var_lst)

    # print(sat_tus)
    # print(var_lst)

    # add for row-all-diff
    for i in range(side_length):
        temp_lst = var_lst[i].copy()
        while len(temp_lst) != 1:
            for index in range(1, len(temp_lst)):
                init_var = temp_lst[0]
                loop_var = temp_lst[index]
                tmp_cos = Constraint((init_var.name + loop_var.name),
                                     [init_var, loop_var])
                tmp_cos.add_satisfying_tuples(sat_tus)
                init_csp.add_constraint(tmp_cos)
            temp_lst.pop(0)

    # add for col-all-diff
    for i in range(side_length):
        for j in range(side_length):
            chose_var = var_lst[j][i]
            for h in range(j):
                loop_var = var_lst[h][i]
                tmp_cos = Constraint((chose_var.name + loop_var.name),
                                     [chose_var, loop_var])
                tmp_cos.add_satisfying_tuples(sat_tus)
                init_csp.add_constraint(tmp_cos)
    return init_csp, var_lst


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
    # instantiate csp
    init_csp = CSP("nary_grid_csp")
    side_length = funpuzz_grid[0][0]
    sat_tus = str_premu_tuple(premu(side_length))
    var_lst = []

    # create NESTED var list
    for i in range(side_length):
        inner_var_lst = []
        for j in range(side_length):
            # add domain as [1 - n]
            tmp_var = Variable(("{}{}".format(i + 1, j + 1)),
                               list(range(1, side_length + 1)))
            inner_var_lst.append(tmp_var)
            init_csp.add_var(tmp_var)

        var_lst.append(inner_var_lst)

    # add for row-diff
    for i in range(side_length):
        tmp_cos = Constraint("Row{}".format(i + 1), var_lst[i])
        tmp_cos.add_satisfying_tuples(sat_tus)
        init_csp.add_constraint(tmp_cos)

    # add for col-diff
    for i in range(side_length):
        col_lst = []
        for j in range(side_length):
            var = var_lst[j][i]
            col_lst.append(var)
        tmp_cos = Constraint("Col{}".format(i + 1), col_lst)
        tmp_cos.add_satisfying_tuples(sat_tus)
        init_csp.add_constraint(tmp_cos)
    return init_csp, var_lst


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

    re_csp, var_lst = binary_ne_grid(funpuzz_grid)

    # Cage constrain
    side_length = funpuzz_grid[0][0]
    for i in range(1, len(funpuzz_grid)):
        cage_var = []
        ops = funpuzz_grid[i][-1]  # int
        target = funpuzz_grid[i][-2]  # int
        grid_var_num = funpuzz_grid[i][0:-2]  # list of int
        # Produce Cage Var_lst
        for j in grid_var_num:
            str_index = str(j)
            row = int(str_index[0])
            col = int(str_index[1])
            cage_var.append(var_lst[row - 1][col - 1])

        tmp_cons = Constraint("Cell{}".format(i), cage_var)

        # Check Operation
        sat_tus = []
        cage_num = len(cage_var)

        if ops == 0:
            sat_tus = combination_sum(cage_num, side_length, target)
        elif ops == 1:
            sat_tus = combination_minor(cage_num, side_length, target)
        elif ops == 2:
            sat_tus = combination_div(cage_num, side_length, target)
        elif ops == 3:
            sat_tus = combination_product(cage_num, side_length, target)

        tmp_cons.add_satisfying_tuples(sat_tus)
        re_csp.add_constraint(tmp_cons)

    return re_csp, var_lst


if __name__ == '__main__':
    b1 = [[3], [11, 21, 3, 0], [12, 22, 2, 1], [13, 23, 33, 6, 3],
          [31, 32, 5, 0]]
    # nary_ad_grid(b1)
    # print(combination_sum(3, 8, 10))
    # print(combination_product(4, 9, 40))
    # print(combination_minor(2, 3, 2))
    # print(combination_div(3, 8, 2))

    # funpuzz_csp_model(b1)
