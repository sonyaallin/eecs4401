#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *


def get_sup_tuples(n):

    sup_tuples = []
    for p in range(1, n + 1):
        for q in range(1, n + 1):
            if p != q:
                sup_tuples.append((p, q))

    return sup_tuples


def add_constraints(n, csp, V, is_column):

    sup_tuples = get_sup_tuples(n)

    for i in range(1, n + 1):
        for j in range(1, n + 1):
            for k in range(j + 1, n + 1):

                if is_column:
                    c = Constraint(get_constraint_name(i, j, k, True), [V[j - 1][i - 1], V[k - 1][i - 1]])
                else:
                    c = Constraint(get_constraint_name(i, j, k, False), [V[i - 1][j - 1], V[i - 1][k - 1]])

                c.add_satisfying_tuples(sup_tuples)
                csp.add_constraint(c)


def get_constraint_name(i, j, k, is_column):

    if is_column:
        return "C-" + str(j) + str(i) + "," + str(k) + str(i)
    else:
        return "R-" + str(i) + str(j) + "," + str(i) + str(k)


def get_variables(n):

    variables = []

    for i in range(1, n + 1):
        variables.append([])
        for j in range(1, n + 1):
            name = get_variable_name(i, j)
            v = Variable(name, list(range(1, n + 1)))
            variables[i - 1].append(v)

    return variables


def get_variable_name(i, j):
    return "V" + str(i) + str(j)

# N-ary helpers

def permute_helper(nums, tuples, assignment):

    if nums == []:
        tuples.append(assignment)
        return

    for num in nums:
        assignment = assignment + (num, )
        new_nums = nums.copy()
        new_nums.remove(num)
        permute_helper(new_nums, tuples, assignment)
        assignment = assignment[:-1]

def permute(n):
    tuples = []
    permute_helper(list(range(1, n + 1)), tuples, ())
    return tuples


def get_constraint_name_nary(num, is_column):

    if is_column:
        return "C" + str(num)
    return "R" + str(num)


def get_scope_nary(V, num, n, is_column):

    scope = []
    for i in range(1, n + 1):

        if is_column:
            scope.append(V[i][num])
        else:
            scope.append(V[num][i])


def permute_cells_helper(n, num_cells, cell_num, perms, perm):

    #print(n, num_cells, cell_num, perms, perm)

    if cell_num >= num_cells:
        perms.append(perm.copy())
        return

    if len(perm) < cell_num + 1:
        perm.append(-1)
    for i in range(1, n + 1):
        perm[cell_num] = i
        permute_cells_helper(n, num_cells, cell_num + 1, perms, perm)


def permute_cells(n, num_cells):

    perms = []
    permute_cells_helper(n, num_cells, 0, perms, [])
    return perms


def meets_target(nums, target, operation):

    if operation == "+":
        return sum(nums) == target
    elif operation == "*":
        return product(nums) == target
    elif operation == "-":
        for num in nums:
            other_nums = nums.copy()
            other_nums.remove(num)
            if num - sum(other_nums) == target:
                return True
        return False
    elif operation == "/":
        for num in nums:
            other_nums = nums.copy()
            other_nums.remove(num)
            if num / product(other_nums) == target:
                return True
        return False
    else:
        print("CUSTOM ERROR: meets_target given an invalid operation")

def product(nums):
    res = 1
    for num in nums:
        res *= num
    return res


def get_target(cage):
    return cage[-2]


def get_operation(cage):
    op = cage[-1]
    if op == 0:
        return "+"
    elif op == 1:
        return "-"
    elif op == 2:
        return "/"
    elif op == 3:
        return "*"
    else:
        print("CUSTOM ERROR: get_operation given an invalid operation number")

def get_scope_cage(cage, V):

    scope = []
    for index in cage[:-2]:
        scope.append(V[int(str(index)[0]) - 1][int(str(index)[1]) - 1])

    return scope



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

    V = get_variables(n)

    variables = []
    for row in V:
        for v in row:
            variables.append(v)

    csp = CSP("Binary", variables)

    add_constraints(n, csp, V, True)
    add_constraints(n, csp, V, False)

    return csp, V


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

    V = get_variables(n)

    variables = []
    for row in V:
        for v in row:
            variables.append(v)

    csp = CSP("N-ary", variables)

    # Add constraints (rows and columns at same ti me)

    for i in (1, n + 1):

        sup_tuples = permute(n)
        c_row = Constraint(get_constraint_name_nary(i, False), get_scope_nary(V, i, n, False))
        c_column = Constraint(get_constraint_name_nary(i, True), get_scope_nary(V, i, n, True))
        c_row.add_satisfying_tuples(sup_tuples)
        c_column.add_satisfying_tuples(sup_tuples)
        csp.add_constraint(c_row)
        csp.add_constraint(c_column)

    return csp, V


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

    #print("FUNPUZZ GRID: " + str(funpuzz_grid))

    csp, V = binary_ne_grid(funpuzz_grid)
    n = funpuzz_grid[0][0]

    cage_num = 1
    for cage in funpuzz_grid[1:]:
        #print("Cage " + str(cage_num) + ": " + str(cage))
        num_cells = len(cage) - 2

        sup_tuples = []
        possible_assignments = permute_cells(n, num_cells)
        #print("Possible assignments: " + str(possible_assignments))

        target = get_target(cage)
        operation = get_operation(cage)
        #print("Target: " + str(target))
        #print("Operation: " + str(operation))

        for asgn in possible_assignments:

            #print("    Assignment: " + str(asgn))
            if meets_target(asgn, target, operation):
                #print("    MEETS")
                sup_tuples.append(tuple(asgn))
            else:
                pass # Put this here for the print statement
                #print("    DOES NOT MEET")


        c = Constraint("Cage_" + str(cage_num), get_scope_cage(cage, V))
        c.add_satisfying_tuples(sup_tuples)

        #print("Satisfying tuples: " + str(sup_tuples))

        csp.add_constraint(c)

        cage_num += 1

    return csp, V

# funpuzz_csp_model([[3], [11, 21, 3, 0], [12, 22, 2, 1], [13, 23, 33, 6, 3], [31, 32, 5, 0]])
