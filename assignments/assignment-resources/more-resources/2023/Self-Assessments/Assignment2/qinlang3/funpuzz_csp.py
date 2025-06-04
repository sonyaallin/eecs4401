#Look for #IMPLEMENT tags in this file.
from itertools import permutations
from itertools import product
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
    d = funpuzz_grid[0][0]
    domain = [i for i in range(1, d+1)]
    satisfying_tuples = list(permutations(domain, 2))
    csp = CSP("csp")
    vs = [[] for i in range(d)]
    for i in range(1, d+1):
        for j in range(1, d+1):
            v = Variable("V"+str(i)+str(j))
            v.add_domain_values(domain)
            csp.add_var(v)
            vs[i-1].append(v)
    for i in range(1, d+1):
        for j in range(1, d+1):
            for k in range(1, d+1):
                if k != j:
                    c = Constraint("C("+str(i)+str(j)+","+str(i)+str(k)+")", [vs[i-1][j-1], vs[i-1][k-1]])
                    c.add_satisfying_tuples(satisfying_tuples)
                    csp.add_constraint(c)
                    c = Constraint("C("+str(j)+str(i)+","+str(k)+str(i)+")", [vs[j-1][i-1], vs[k-1][i-1]])
                    c.add_satisfying_tuples(satisfying_tuples)
                    csp.add_constraint(c)
    return csp, vs


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
    d = funpuzz_grid[0][0]
    domain = [i for i in range(1, d+1)]
    csp = CSP("csp")
    vs = [[] for i in range(d)]
    for i in range(1, d+1):
        for j in range(1, d+1):
            v = Variable("V"+str(i)+str(j))
            v.add_domain_values(domain)
            csp.add_var(v)
            vs[i-1].append(v)
        
    satisfying_tuples = list(permutations(domain))
    for i in range(len(satisfying_tuples)):
        satisfying_tuples[i] = tuple(satisfying_tuples[i])

    for i in range(1, d+1):
        c = Constraint("C(row"+str(i)+")", vs[i-1])
        c.add_satisfying_tuples(satisfying_tuples)
        csp.add_constraint(c)
        scope_lst = []
        for j in range(1, d+1):
            scope_lst.append(vs[j-1][i-1])
        c = Constraint("C(col"+str(i)+")", scope_lst)
        c.add_satisfying_tuples(satisfying_tuples)
        csp.add_constraint(c)
    return csp, vs



def minus(tuple, target):
    """
    helper function, return True if tuple satisfy target using subtract
    """
    lst = list(permutations(tuple, len(tuple)))
    for t in lst:
        result = t[0]
        for i in range(1, len(t)):
            result = result-t[i]
        if result == target:
            return True
    return False

def multiply(tuple, target):
    """
    helper function, return True if tuple satisfy target using multiply
    """
    result = 1
    for num in tuple:
        result = result * num
    return result == target

def divide(tuple, target):
    """
    helper function, return True if tuple satisfy target using divide
    """
    lst = list(permutations(tuple, len(tuple)))
    for t in lst:
        result = t[0]
        for i in range(1, len(t)):
            result = result/t[i]
        if result == target:
            return True
    return False

def update_satisfying_tuples(satisfying_tuples, op, target):
    """
    helper function, return satisfying_tuples given opeartion and target 
    """
    if op == 0:
        return [tuple for tuple in satisfying_tuples if sum(tuple) == target]
    elif op == 1:
        return [tuple for tuple in satisfying_tuples if minus(tuple, target)]
    elif op == 2:
        return [tuple for tuple in satisfying_tuples if divide(tuple, target)]
    elif op == 3:
        return [tuple for tuple in satisfying_tuples if multiply(tuple, target)]


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
    csp, vars = binary_ne_grid(funpuzz_grid)    # choose binary binary not-equal
    #csp, vars = nary_ad_grid(funpuzz_grid)
    d = funpuzz_grid[0][0]
    domain = [i for i in range(1, d+1)]
    for i in range(1, len(funpuzz_grid)):
        lst = funpuzz_grid[i]
        target = lst[-2]
        op = lst[-1]
        scope = []
        name = "C "
        for j in range(0, len(lst)-2):
            row_idx = int(str(lst[j])[0])-1
            col_idx = int(str(lst[j])[1])-1
            scope.append(vars[row_idx][col_idx])
            name += str(lst[j])+" "
        c = Constraint(name, scope)
        satisfying_tuples = list(product(domain, repeat = len(lst)-2))
      
        c.add_satisfying_tuples(update_satisfying_tuples(satisfying_tuples, op, target))
        csp.add_constraint(c)

    return csp, vars


