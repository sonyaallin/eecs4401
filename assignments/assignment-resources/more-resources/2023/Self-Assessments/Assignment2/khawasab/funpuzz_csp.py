# Look for #IMPLEMENT tags in this file.

""" Construct and return funpuzz CSP models. """

from cspbase import *


def binary_ne_grid(funpuzz_grid):  # DONE
    """A model of a funpuzz grid (without cage constraints) built using only
    binary all-different constraints for both the row and column constraints.

    Returns a CSP object representing a FunPuzz Grid CSP problem along with an
    array of variables for the problem. That is return:

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using binary
    constraints to enforce row and column constraints and variable_array is a
    list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to
    represent the value to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """

    sz = funpuzz_grid[0][0]  # This is the size of the grid. Constraints dont
    # matter.

    dom, new_vars, consts = [], [], list(range(1, sz + 1))

    for ten in range(1, sz + 1):
        for unit in range(1, sz + 1):
            new_num = str(ten * 10 + unit)
            new_vars.append(Variable(str(new_num), dom))
        # The last sz elements are in the same dimention so lets create the
        # constraints for those.
        consts.extend(bin_neq_consts(sz, new_vars[-1 * sz:]))
    # Now the row constraints are taken care of. Lets do the Columns

    # Now new_vars is complete, we just need to do the columns

    for i in range(sz):
        temp = []  # This is per column
        for j in range(sz):
            temp.append(new_vars[j * sz + i])
        consts.extend(bin_neq_consts(sz, temp))

    csp = CSP("Final CSP", new_vars)
    for c in consts:
        csp.add_constraint(c)

    final = []

    for i in range(sz):
        final.append(new_vars[i * sz: (i + 1) * sz])

    return csp, final


def bin_neq_consts(size, dim):
    """
    size is the size of the grid (and thus the size of dim). dim is a list of
    size variables that must all not equal each other. return a list of
    constraints.
    """

    final = []

    for i in range(size):
        for j in range(size - i - 1):
            var1, var2 = dim[i], dim[j + i + 1]
            const_name = var1.name() + " vs " + var2.name
            temp_scope = [var1, var2]
            temp_const = Constraint(const_name, temp_scope)
            for item1 in var1.domain():
                for item2 in var2.domain():
                    if item1 != item2:
                        temp_const.add_satisfying_tuples((item1, item2))

            # Now temp_const is a temporary constraint with all of the
            # satisfying tuples
            final.append(temp_const)

    return final


def nary_ad_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only
    n-ary all-different constraints for both the row and column constraints.

    Returns a CSP object representing a Cageoky Grid CSP problem along with an
    array of variables for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using n-ary constraints
    to enforce row and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to
    represent the value to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """

    sz = funpuzz_grid[0][0]  # This is the size of the grid. Constraints dont
    # matter.

    dom, new_vars, consts = list(range(1, sz + 1)), [], list(range(1, sz + 1))

    for ten in range(1, sz + 1):
        for unit in range(1, sz + 1):
            new_num = str(ten * 10 + unit)
            new_vars.append(Variable(new_num, dom))
        # The last sz elements are in the same dimention so lets create the
        # constraints for those.
        consts.append(n_neq_consts(sz, new_vars[-1 * sz:], "Row #" + str(ten)))
    # Now the row constraints are taken care of. Lets do the Columns

    # Now new_vars is complete, we just need to do the columns

    for i in range(sz):
        temp = []  # This is per column
        for j in range(sz):
            temp.append(new_vars[j * sz + i])
        consts.append(n_neq_consts(sz, temp, "Column #" + str(i)))

    csp = CSP("Final CSP", new_vars)
    # print(consts)
    for c in consts:
        # print(f'Adding Constraint: {c}')
        csp.add_constraint(c)

    final = []

    for i in range(sz):
        final.append(new_vars[i * sz: (i + 1) * sz])

    return csp, final


def n_neq_consts(size, dim, name):
    const_tups = n_neq_consts_helper(size, dim)
    const = Constraint(name, dim)

    # print(f'Number of satisfying tuples for {name}: {len(const_tups)}')

    const.add_satisfying_tuples(const_tups)

    return const


def n_neq_consts_helper(size, dim):
    """
    size is the size of the grid (and thus the size of dim). dim is a list of
    size variables that must all not equal each other. return a list of
    satisfying tuple permutations.
    """
    if size == 0:  # Base Case: dim is empty
        return [()]

    one_less = n_neq_consts_helper(size - 1, dim[: -1])

    final = []

    for tup in one_less:
        for elem in dim[-1].domain():
            if elem not in tup:
                temp = list(tup)
                temp.append(elem)
                final.append(tuple(temp))

    return final


def num_to_var_helper(var_num, vars_lst):
    for var in vars_lst:
        if var.name == str(var_num):
            return var
    return None


def accum(poss, op):
    """
    Given a set of assignmnets, find the accumulation of op on poss
    """
    if len(poss) == 1:
        return poss[0]
    return op(accum(poss[:-1], op), poss[-1])


def find_valid_asgns(all_poss, acc, op):
    """
    This will take a list of all permutations of variable assignments, and see
    whether applying a certain operation on these permuations sequentially will
    return the acc
    """

    final = []

    for poss in all_poss:
        if accum(poss, op) == acc:
            final.append(tuple(poss))

    return final


def permute(const_vars):
    """
    Create every permutation of this list of variables.
    """
    if len(const_vars) == 0:
        return [[]]

    final = []
    one_less = permute(const_vars[1:])

    for perm in one_less:
        for i in range(len(const_vars)):
            temp = perm.copy()
            final.append(temp[:i] + [const_vars[0]] + temp[i:])
    return final


def funpuzz_csp_model(funpuzz_grid):
    """A model built using your choice of (1) binary binary not-equal, or (2)
    n-ary all-different constraints for the grid, together with (3) funpuzz cage
    constraints. That is, you will choose one of the previous two grid models
    and expand it to include cage constraints for the funpuzz Variation.

    Returns a CSP object representing a Cageoky Grid CSP problem along with an
    array of variables for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using constraints
    to enforce cage, row and column constraints and variable_array is a list of
    lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to
    represent the value to be placed in cell i,j of the funpuzz Grid.

    Note that this model does require implementation of cage constraints.
    """

    """
    Basically we want to just call one of the above functions weve implements. 
    Then we want to cycle through the constraints, for each one, access the
    variable that has already been created with that name, make a constraint 
    with the necessary satisfying tuples, and add them to the csp
    """

    sz = funpuzz_grid[0][0]

    csp, vars = nary_ad_grid(funpuzz_grid)

    temp = []

    for var_row in vars:
        temp.extend(var_row)

    vars = temp

    for i, const in enumerate(funpuzz_grid[1:]):
        const_vars = []
        for nar_num in const[: -2]:
            const_vars.append(num_to_var_helper(nar_num, vars))

        # Now cons_vars is a list of all variables in scope of this condition.

        acc, op = const[-2:]  # Accumulator and operation
        op = get_op(op)  # Now op is a function that does what op refers to

        all_poss = perm_creator(len(const[:-2]), const_vars[0].domain())
        valid = find_valid_asgns(all_poss, acc, op)
        # Now valid refers to all the satisfying tuples of the constraint

        variables_permutations = permute(const_vars)

        for j, perm in enumerate(variables_permutations):
            name = "RealConstraint #" + str(i + 1) + " Iteration #" + str(j + 1)
            temp = Constraint(name, perm)
            temp.add_satisfying_tuples(valid)

            csp.add_constraint(temp)  # Add this constraint to the csp

    final = []

    for i in range(sz):
        final.append(vars[i * sz: (i + 1) * sz])

    return csp, final


def perm_creator(num, dom):
    """
    Given a domain, and the number of variables tha have this domain, create
    every single set of variable assignments. will return a list of lists where
    the total number of elements is num^2
    """
    if num == 0:
        return [[]]

    final = []
    one_less = perm_creator(num-1, dom)

    for elem in dom:
        for sec_elem in one_less:
            temp = sec_elem.copy()
            temp.append(elem)
            final.append(temp)
    return final


def get_op(op_num):
    if op_num == 0:
        return add
    elif op_num == 1:
        return subt
    elif op_num == 2:
        return div
    else:
        return mult


def add(num1, num2):
    return num1 + num2


def mult(num1, num2):
    return num1 * num2


def subt(num1, num2):
    return num1 - num2


def div(num1, num2):
    return num1 / num2
