#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import numpy as np
from itertools import permutations, product
import functools as ft
import operator

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
    domain = np.arange(start=1, stop=n+1)    
    variable_array = np.array([[Variable(f'Row = {i+1} Col = {j+1}', domain=domain) for j in range(n)] for i in range(n)])
    funpuzz_csp = CSP('Binary NE CSP', variable_array.flatten())
    perm_2 = list(permutations(domain, 2))
    for i in range(n): 
       row = variable_array[i]
       for j in range(n):
          variable = row[j]
          # loop through row
          for k in range(n):
             if k != j:
                row_constraint = Constraint(f'arr[{i}, {j}] != arr[{i}, {k}]', [variable, variable_array[i, k]])
                row_constraint.add_satisfying_tuples(perm_2)
                funpuzz_csp.add_constraint(row_constraint)

          # loop through column
          for k in range(n):
             if k != i:
                col_constraint = Constraint(f'arr[{i}, {j}] != arr[{k}, {j}]', [variable, variable_array[k, j]])
                col_constraint.add_satisfying_tuples(perm_2)
                funpuzz_csp.add_constraint(col_constraint)

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
    n = funpuzz_grid[0][0]
    domain = np.arange(start=1, stop=n+1)    
    variable_array = np.array([[Variable(f'Row = {i+1} Col = {j+1}', domain=domain) for j in range(n)] for i in range(n)])
    funpuzz_csp = CSP('Binary NE CSP', variable_array.flatten())
    perm_n = list(permutations(domain))
    for i in range(n): 
        row_constraint = Constraint(f'All not equal row {i}', variable_array[i, :])
        row_constraint.add_satisfying_tuples(perm_n)
        funpuzz_csp.add_constraint(row_constraint)
        col_constraint = Constraint(f'All not equal col {i}', variable_array[:, i])
        col_constraint.add_satisfying_tuples(perm_n)
        funpuzz_csp.add_constraint(col_constraint)

    return funpuzz_csp, variable_array

def check_perm_result(perm, op, target, save):
    result = 0
    if op == 0:
        result = ft.reduce(operator.add, perm, result)
    elif op == 3:
        result = 1
        result = ft.reduce(operator.mul, perm, result)
    elif op == 1:
        if perm in save:
            return True
        perms = list(permutations(perm))
        for permutation in perms:
            result = permutation[0]
            for i in range(1, len(perm)):
                result -= permutation[i]
            if result == target:
                for p in perms:
                    save[p + tuple(["-"])] = True
                return True              
        
    elif op == 2:
        if perm in save:
            return True
        perms = list(permutations(perm))
        for permutation in perms:
            result = permutation[0]
            for i in range(1, len(perm)):
                result /= permutation[i]
            if result == target:
                for p in perms:
                    save[p + tuple(["/"])] = True
                return True   
    return target == result


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
    n = funpuzz_grid[0][0]
    domain = np.arange(start=1, stop=n+1) 
    funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)
    funpuzz_csp.name = "FunPuzz Full CSP"
    save = {}
    for i in range(1, len(funpuzz_grid)):
        funpuzz_cons = funpuzz_grid[i]
        if len(funpuzz_cons) == 2:
            row = funpuzz_cons[0] // 10 - 1
            col = funpuzz_cons[0] % 10 - 1
            target = funpuzz_cons[1]
            variables = [variable_array[row, col]]
            constraint = Constraint(f'Funpuzz Constraint {i}', variables)
            constraint.add_satisfying_tuples([[target]])
            funpuzz_csp.add_constraint(constraint)
            continue

        operation = funpuzz_cons[-1]
        target = funpuzz_cons[-2]
        scope_size = len(funpuzz_cons) - 2
        variables = []
        perm_funpuzz = list(product(domain, repeat=scope_size))
        perm_funpuzz = list(filter(lambda x: check_perm_result(x, operation, target, save), perm_funpuzz))
        for j in range(scope_size):
            row = funpuzz_cons[j] // 10 - 1
            col = funpuzz_cons[j] % 10 - 1
            variable_array[row, col]
            variables.append(variable_array[row, col])
        constraint = Constraint(f'Funpuzz Constraint {i}', variables)
        constraint.add_satisfying_tuples(perm_funpuzz)
        funpuzz_csp.add_constraint(constraint)

    return funpuzz_csp, variable_array



if __name__=="__main__":
    #Sanity checks
    sample = [[4], [11, 21, 6, 3], [12, 13, 3, 0], [14, 24, 3, 1], [22, 23, 7, 0], [31, 32, 2, 2], [33, 43, 3, 1],
           [34, 44, 6, 3], [41, 42, 7, 0]]
    csp, arr = funpuzz_csp_model(sample)
    for key in csp.vars_to_cons:
        item = csp.vars_to_cons[key]
        print(key, len(item), item[0].name, len(item[1].sat_tuples))
