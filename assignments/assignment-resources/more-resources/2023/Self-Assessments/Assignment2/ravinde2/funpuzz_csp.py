#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations, combinations, product
import math

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
    size = funpuzz_grid[0][0]
    var_list = []
    variable_array = x = [ [[i] for i in range(size)] for i in range(size) ]
    tuples = []
    funpuzz_csp = CSP("funpuzz_cps")
    
    for w in range(1, size + 1):
        for g in range(1, size + 1):
            if w != g:
                tuples.append((w, g))
          
    for i in range(size):
        for y in range(size):
            var = Variable(str(i) + str(y), list(range(1, size + 1)))
            var_list.append(var)
            variable_array[i][y] = var
            funpuzz_csp.add_var(var)

    for i in range(size):
        for y in range(size):
            for t in range(y, size):
                cons = Constraint(str(i) + str(y), list((variable_array[i][y], variable_array[i][t])))
                cons.add_satisfying_tuples(tuples.copy())
                funpuzz_csp.add_constraint(cons)
    for i in range(size):
        for y in range(size):
            for t in range(y, size):
                cons = Constraint(str(i) + str(y), list((variable_array[y][i], variable_array[t][i])))
                cons.add_satisfying_tuples(tuples.copy())
                funpuzz_csp.add_constraint(cons)
            
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
    size = funpuzz_grid[0][0]
    var_list = []
    variable_array = x = [ [[i] for i in range(size)] for i in range(size) ]
    variable_array_col = x = [ [[i] for i in range(size)] for i in range(size) ]
    tuples = []
    funpuzz_csp = CSP("funpuzz_cps")
    
    tuples = list(permutations(range(1, size + 1), size))
                
    for i in range(size):
        row_var = []
        for y in range(size):
            var = Variable(str(i) + str(y), list(range(1, size + 1)))
            var_list.append(var)
            variable_array[i][y] = var
            variable_array_col[y][i] = var
            row_var.append(var)
            funpuzz_csp.add_var(var)
        cons = Constraint("Row" + str(i), row_var.copy())
        cons.add_satisfying_tuples(tuples.copy())
        funpuzz_csp.add_constraint(cons)
    
    for col in variable_array_col:
        cons = Constraint("Col" + str(i), col)
        cons.add_satisfying_tuples(tuples.copy())
        funpuzz_csp.add_constraint(cons)
    print(variable_array)
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
    size = funpuzz_grid[0][0]
    var_list = []
    variable_array = x = [ [[i] for i in range(size)] for i in range(size) ]
    variable_array_col = x = [ [[i] for i in range(size)] for i in range(size) ]
    row_tuples = list(permutations(range(1, size + 1), size))
    funpuzz_csp = CSP("funpuzz_cps")

    for i in range(1, len(funpuzz_grid)):
        counter = 0
        var_scope = []
        for y in range(len(funpuzz_grid[i]) - 1):
            if y < len(funpuzz_grid[i]) - 2:
                var = Variable(str(funpuzz_grid[i][y]), range(1, size + 1))
                var_scope.append(var)
                var_list.append(var)
                variable_array[(funpuzz_grid[i][y] // 10) - 1][(funpuzz_grid[i][y] % 10) - 1] = var
                variable_array_col[(funpuzz_grid[i][y] % 10) - 1][(funpuzz_grid[i][y] // 10) - 1] = var
                funpuzz_csp.add_var(var)
                counter += 1
            else:
                sign = funpuzz_grid[i][y + 1]
                target = funpuzz_grid[i][y]
                if sign == 0:
                    valid_sol = [pair for pair in product(list(range(1,size + 1)), repeat=counter) if sum(pair) == target]
                elif sign == 1:
                    valid_sol = [pair for pair in product(list(range(1,size + 1)), repeat=counter) if initial_sub(pair, target)]
                elif sign == 2:
                    valid_sol = [pair for pair in product(list(range(1,size + 1)), repeat=counter) if initial_div(pair, target)] 
                else:
                    valid_sol = [pair for pair in product(list(range(1,size + 1)), repeat=counter) if math.prod(pair) == target]
                cons = Constraint("Cage" + str(i), var_scope)
                cons.add_satisfying_tuples(valid_sol.copy())
                funpuzz_csp.add_constraint(cons)

    for row in variable_array:
        cons = Constraint("Row" , row)
        cons.add_satisfying_tuples(row_tuples.copy())
        funpuzz_csp.add_constraint(cons)

    for col in variable_array_col:
        cons = Constraint("Col" , col)
        cons.add_satisfying_tuples(row_tuples.copy())
        funpuzz_csp.add_constraint(cons)

    return funpuzz_csp, variable_array

def total_sum(array, num):
    result = []
    def find(arr, num, path=()):
        if not arr:
            return
        if arr[0] == num:
            result.append(path + (arr[0],))
        else:
            find(arr[1:], num - arr[0], path + (arr[0],))
            find(arr[1:], num, path)
    find(array, num)
    return result


def initial_sub(lst, target):
    tracker = False
    lst = list(lst)
    for i in lst:
        head = i
        new_lst = lst.copy()
        new_lst.remove(i)
        tracker = tracker or sub(new_lst, target, head)
    return tracker
def sub(lst, target, head):
    
    if head == target and lst == []:
        return True
    elif lst == []:
        return False
    else:
        tracker = False
        for i in lst:
            new_lst = lst.copy()
            new_lst.remove(i)
            tracker = tracker or sub(new_lst, target, head - i)
        return tracker


def initial_div(lst, target):
    tracker = False
    lst = list(lst)
    for i in lst:
        head = i
        new_lst = lst.copy()
        new_lst.remove(i)
        tracker = tracker or div(new_lst, target, head)
    return tracker
def div(lst, target, head):
    
    if head == target and lst == []:
        return True
    elif lst == []:
        return False
    else:
        tracker = False
        for i in lst:
            new_lst = lst.copy()
            new_lst.remove(i)
            tracker = tracker or div(new_lst, target, head / i)
        return tracker




