# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations, combinations_with_replacement


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
    var_arr = []
    domain = list(range(1, n + 1))
    csp_obj = CSP(str(n))
    # Add variables
    for x in range(1, n + 1):
        var_arr.append([])
        for y in range(1, n + 1):
            new_var = Variable(str(x * 10 + y), domain)
            var_arr[x - 1].append(new_var)
            csp_obj.add_var(new_var)

    # Add row constraints
    for x in range(n):
        for y in range(n):
            curr_var = var_arr[x][y]
            for y2 in range(y + 1, n):
                other_var = var_arr[x][y2]
                row_cons = Constraint(curr_var.name + '!=' + other_var.name, [curr_var, other_var])
                # create satisfying tuples
                tup = []
                for a in domain:
                    for b in domain:
                        if a != b:
                            tup.append((a, b))
                row_cons.add_satisfying_tuples(tup)
                csp_obj.add_constraint(row_cons)
    # Add column constraints
    for y in range(n):
        for x in range(n):
            curr_var = var_arr[x][y]
            for x2 in range(x + 1, n):
                other_var = var_arr[x2][y]
                col_cons = Constraint(curr_var.name + '!=' + other_var.name, [curr_var, other_var])
                # create satisfying tuples
                tup = []
                for a in domain:
                    for b in domain:
                        if a != b:
                            tup.append((a, b))
                col_cons.add_satisfying_tuples(tup)
                csp_obj.add_constraint(col_cons)
    return csp_obj, var_arr


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
    var_arr = []
    domain = list(range(1, n + 1))
    csp_obj = CSP(str(n))
    # Add variables
    for x in range(1, n + 1):
        var_arr.append([])
        for y in range(1, n + 1):
            new_var = Variable(str(x * 10 + y), domain)
            var_arr[x - 1].append(new_var)
            csp_obj.add_var(new_var)

    # Add row constraints
    for x in range(n):
        scope = []
        cons_name = ''
        for y in range(n):
            curr_var = var_arr[x][y]
            scope.append(curr_var)
            cons_name += curr_var.name + '!='
        row_cons = Constraint(cons_name, scope)
        # create satisfying tuples
        row_cons.add_satisfying_tuples(list(permutations(domain)))
        csp_obj.add_constraint(row_cons)
    # Add column constraints
    for y in range(n):
        scope = []
        cons_name = ''
        for x in range(n):
            curr_var = var_arr[x][y]
            scope.append(curr_var)
            cons_name += curr_var.name + '!='
        col_cons = Constraint(cons_name, scope)
        # create satisfying tuples
        col_cons.add_satisfying_tuples(list(permutations(domain)))
        csp_obj.add_constraint(col_cons)
    return csp_obj, var_arr


def add(nums):
    return sum(nums)


def subtract(nums):
    start = nums[0]
    for i in range(1, len(nums)):
        start -= nums[i]
    return start


def product(nums):
    start = nums[0]
    for i in range(1, len(nums)):
        start = start * nums[i]
    return start


def quotient(nums):
    start = nums[0]
    for i in range(1, len(nums)):
        start = start / nums[i]
    return start


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
    csp_obj, var_arr = binary_ne_grid(funpuzz_grid)
    n = funpuzz_grid[0][0]
    domain = list(range(1, n + 1))
    for c in range(1, len(funpuzz_grid)):
        # Retrieve all relevant values
        curr_cage = funpuzz_grid[c]
        curr_op = curr_cage[-1]
        curr_target = curr_cage[-2]
        curr_vars = []
        curr_cons_name = ''
        # Retrieve vars from var_arr
        for var in range(len(curr_cage) - 2):
            x = curr_cage[var] // 10
            y = curr_cage[var] % 10
            curr_vars.append(var_arr[x - 1][y - 1])
            curr_cons_name += ((var_arr[x - 1][y - 1]).name + ' ')
        # Construct name and create constraint
        curr_cons_name += str(curr_op) + ' '+ str(curr_target)
        curr_cons = Constraint(curr_cons_name, curr_vars)
        # All possible combinations with replacement of domain
        possible_sups = list(combinations_with_replacement(domain, r=len(curr_vars)))
        final_sups = []
        for sup in possible_sups:
            # All possible ways of arranging these numbers as we can order variables in any fashion
            possible_inputs = list(permutations(sup))
            for input in possible_inputs:
                result = None
                if curr_op == 0:
                    result = add(input)
                elif curr_op == 1:
                    result = subtract(input)
                elif curr_op == 2:
                    result = quotient(input)
                elif curr_op == 3:
                    result = product(input)
                if result == curr_target:
                    possible_inputs = list(possible_inputs)
                    final_sups.extend(possible_inputs)
                    break
        curr_cons.add_satisfying_tuples(final_sups)
        csp_obj.add_constraint(curr_cons)
    return csp_obj, var_arr
