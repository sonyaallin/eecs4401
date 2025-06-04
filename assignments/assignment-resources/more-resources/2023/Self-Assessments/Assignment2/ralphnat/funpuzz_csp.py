#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools as t


def create_lst(n):
    """
    Returns list of variables
    """
    var_lst = []
    dom_lst = []

    for i in range(1, n + 1):
        dom_lst.append(i)

    for i in range(1, n + 1):
        temp_lst = []
        for j in range(1, n + 1):
            # Var1
            temp_var = Variable(str(i) + str(j), dom_lst)
            temp_lst.append(temp_var)
        var_lst.append(temp_lst)
    return var_lst

'''
def get_row_cons(var_lst):
    """
    Returns list of row contraints
    """
    cons_lst = []
    for x in var_lst:
        temp = tuple(x)
        cons_lst.append(Constraint(x.name, temp))
    return cons_lst
'''


def get_bincons(var_lst):
    """
    Returns a list of Binary constraints
    """
    tup_lst = []
    cons_lst = []
    n = len(var_lst)
    # Get contraint tuples
    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if (j != k):
                    tup1 = tuple([var_lst[i][j], var_lst[i][k]])
                    tup2 = tuple(reversed(tup1))
                    tup3 = tuple([var_lst[j][i], var_lst[k][i]])
                    tup4 = tuple(reversed(tup1))
                    if not (tup1 in tup_lst or tup2 in tup_lst or tup3 in tup_lst or tup4 in tup_lst):
                        tup_lst.append(tup1)
                        tup_lst.append(tup3)

    for con in tup_lst:
        cons_lst.append(Constraint(str(con), con))
    return cons_lst


def get_ncons(var_lst, n):
    """
    Returns a list of n-ary constraints
    """
    tup_lst = []
    cons_lst = []
    # Get row constraints
    for row in var_lst:
        tup_lst.append(tuple(row))

    for i in range(0, n):
        temp_lst = []
        for j in range(0, n):
            temp_lst.append(var_lst[j][i])
        tup_lst.append(tuple(temp_lst))

    for con in tup_lst:
        cons_lst.append(Constraint(str(con), con))

    return cons_lst


def add_tuples(cons_lst, num_size, n):
    """
    Adds satisyfing tuples to constraints in cons_lst
    """
    value_lst = []

    for i in range(1, num_size + 1):
        value_lst.append(i)

    for con in cons_lst:  # Add satisying constraints
        sat_lst = list(t.permutations(value_lst, n))
        con.add_satisfying_tuples(sat_lst)


def get_cagecons(var_lst, grid):
    """
    Returns a list of cage constraints
    """
    cons_lst = []
    tup_lst = []
    for i in range(1, len(grid)):
        cage = grid[i]
        # Go through cage, find vars -> Add to tuples (Worry about possible values later)
        temp_lst = []
        for x in cage:
            for table in var_lst:
                for var in table:
                    if (str(x) == var.name):
                        # Add var to lst
                        temp_lst.append(var)
        tup_lst.append(tuple(temp_lst))

    for con in tup_lst:
        cons_lst.append(Constraint(str(con), con))
    return cons_lst


def plus_tuples(con, va, dom):
    """
    Adds satisfying tuples for addition operation
    """
    tup_lst = []
    n = len(con.get_scope())  # Number of vars in the scope
    pos_vals = list(t.permutations(dom, n))

    for perm in pos_vals:
        if (sum(perm) == va):
            tup_lst.append(perm)

    con.add_satisfying_tuples(tup_lst)


def sub_tuples(con, va, dom):
    """
    Adds satisfying tuples for subtraction operation
    """
    tup_lst = []
    n = len(con.get_scope())  # Number of vars in the scope
    pos_vals = list(t.permutations(dom, n))

    for perm in pos_vals:
        sub_num = perm[0]
        for i in range(1, len(perm)):
            sub_num -= perm[i]
        if (sub_num == va):
            tup_lst.extend(list(t.permutations(perm, len(perm))))

    con.add_satisfying_tuples(tup_lst)


def div_tuples(con, va, dom):
    """
    Adds satisfying tuples for division operation
    """
    tup_lst = []
    n = len(con.get_scope())  # Number of vars in the scope
    pos_vals = list(t.permutations(dom, n))

    for perm in pos_vals:
        div_num = perm[0]
        for i in range(1, len(perm)):
            div_num /= perm[i]
        if (div_num == va):
            tup_lst.extend(list(t.permutations(perm, len(perm))))

    con.add_satisfying_tuples(tup_lst)


def mult_tuples(con, va, dom):
    """
    Adds satisfying tuples for multiplication operation
    """
    tup_lst = []
    n = len(con.get_scope())  # Number of vars in the scope
    pos_vals = list(t.permutations(dom, n))

    for perm in pos_vals:
        mult_num = perm[0]
        for i in range(1, len(perm)):
            mult_num *= perm[i]
        if (mult_num == va):
            tup_lst.append(perm)

    con.add_satisfying_tuples(tup_lst)


def add_cage_tuples(cons_lst, grid, dom):
    """
    Adds satisfying tuples given by grid to constraints in cons_lst
    """
    op_lst = []   # List of operations of each cage
    sat_lst = []  # List for satisyfing values of each cage
    for i in range(1, len(grid)):
        op_lst.append(grid[i][-1])
        sat_lst.append(grid[i][-2])

    # Loop through constraints
    for i in range(0, len(cons_lst)):
        # check operations
        if (op_lst[i] == 0):
            plus_tuples(cons_lst[i], sat_lst[i], dom)  # Addition
        elif (op_lst[i] == 1):
            sub_tuples(cons_lst[i], sat_lst[i], dom)  # Subtraction
        elif (op_lst[i] == 2):
            div_tuples(cons_lst[i], sat_lst[i], dom)  # Division
        elif (op_lst[i] == 3):
            mult_tuples(cons_lst[i], sat_lst[i], dom)  # Multiplication


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
    num_size = funpuzz_grid[0][0]  # Size of the Sudoku grid

    var_lst = create_lst(num_size)
    cons_lst = get_bincons(var_lst)
    add_tuples(cons_lst, num_size, 2)
    # cons_lst.extend(get_col_cons(var_lst))
    fun_csp = CSP("Binary FunPuzz")

    for x in var_lst:
        for var in x:
            fun_csp.add_var(var)

    for con in cons_lst:
        fun_csp.add_constraint(con)

    return fun_csp, var_lst


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
    num_size = funpuzz_grid[0][0]  # Size of the Sudoku grid
    var_lst = create_lst(num_size)
    fun_csp = CSP("n-ary FunPuzz")
    cons_lst = get_ncons(var_lst, num_size)
    add_tuples(cons_lst, num_size, num_size)
    for x in var_lst:
        for var in x:
            fun_csp.add_var(var)

    for con in cons_lst:
        fun_csp.add_constraint(con)

    return fun_csp, var_lst


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
    num_size = funpuzz_grid[0][0]  # Size of the Sudoku grid
    fun_csp, var_lst = binary_ne_grid(funpuzz_grid)

    # Create constraints
    cons_lst = get_cagecons(var_lst, funpuzz_grid)
    add_cage_tuples(cons_lst, funpuzz_grid, var_lst[0][0].domain())

    for con in cons_lst:
        fun_csp.add_constraint(con)

    return fun_csp, var_lst


