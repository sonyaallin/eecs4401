#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations
from itertools import combinations_with_replacement

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
    
    size = (funpuzz_grid[0])[0]
    
    variable_domain = list()
    variables = list()
    csp_result = CSP("FUNPUZZ")
    s_tuples = list()
    
    for i in range(size):
        variables.append([])
        for j in range(size):
            variables[i].append(None)
            if i != j:
                s_tuples.append((i+1,j+1))
    
    for i in range(size):
        variable_domain.append(i+1)
    
    for i in range(size):
        for j in range(size):
            new_v = Variable(str(i+1)+str(j+1),variable_domain)
            variables[i][j] = new_v
            csp_result.add_var(new_v)
    
    for i in range(size):
        for j in range(size):
            for k in range(i+1, size):
                con = Constraint(str(i+1)+str(j+1)+","+str(k+1)+str(j+1), [variables[i][j],variables[k][j]])
                con.add_satisfying_tuples(s_tuples)
                csp_result.add_constraint(con)
            for l in range(j+1, size):
                con = Constraint(str(i+1)+str(j+1)+","+str(i+1)+str(l+1), [variables[i][j],variables[i][l]])
                con.add_satisfying_tuples(s_tuples)
                csp_result.add_constraint(con)
                
    return csp_result, variables

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
    
    size = (funpuzz_grid[0])[0]
    
    variable_domain = list()
    variables = list()
    csp_result = CSP("FUNPUZZ")
    s_tuples = list()
    
    for i in range(size):
        variables.append([])
        for j in range(size):
            variables[i].append(None)
    
    for i in range(size):
        variable_domain.append(i+1)
    
    perm = permutations(variable_domain)
    for p in perm:
        s_tuples.append(tuple(p))
    
    for i in range(size):
        for j in range(size):
            new_v = Variable(str(i+1)+str(j+1),variable_domain)
            variables[i][j] = new_v
            csp_result.add_var(new_v)
    
    for i in range(size):
        
        scope_col = list()
        scope_row = list()
        
        for j in range(size):
            scope_col.append(variables[j][i])
            scope_row.append(variables[i][j])
        
        con_col = Constraint("Column "+ str(i+1), scope_col)
        con_row = Constraint("Row "+ str(i+1), scope_row)
        con_col.add_satisfying_tuples(s_tuples)
        con_row.add_satisfying_tuples(s_tuples)
        csp_result.add_constraint(con_col)
        csp_result.add_constraint(con_row)
                
    return csp_result, variables


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
    
    
    csp_result, variables = nary_ad_grid(funpuzz_grid)
    
    size = (funpuzz_grid[0])[0]
    
    for i in range(1,len(funpuzz_grid)):
        scope = list()
        for j in range(len(funpuzz_grid[i])-2):
            for k in range(size):
                for l in range(size):
                    if variables[k][l].name == str(funpuzz_grid[i][j]):
                        scope.append(variables[k][l])
       
        s_tuples = list()
        result = funpuzz_grid[i][-2]
        operation = funpuzz_grid[i][-1]
        values = list()
        
        for j in range(size):
            values.append(j+1)
        
        values_p = list(combinations_with_replacement(values,len(funpuzz_grid[i])-2))
        
        for perm in values_p:
            if operation == 0:              
                tsum = 0
                for num in perm:
                    tsum += num
                if tsum == result:
                    perms = permutations(perm)
                    for new_perm in perms:
                        if new_perm not in s_tuples:
                            s_tuples.append(tuple(new_perm))
            elif operation == 1:
                perms = permutations(perm)
                for new_perm in perms:
                    tsub = new_perm[0]
                    for j in range(1,len(new_perm)):
                        tsub -= new_perm[j]
                    if abs(tsub) == result and new_perm not in s_tuples:
                        s_tuples.append(tuple(new_perm))
            elif operation == 2:
                perms = permutations(perm)
                for new_perm in perms:
                    tdiv = new_perm[0]
                    for j in range(1,len(new_perm)):
                        tdiv = tdiv/new_perm[j]
                    if tdiv == result and new_perm not in s_tuples:
                        s_tuples.append(tuple(new_perm))
                        s_tuples.append((new_perm[1],new_perm[0]))
            elif operation == 3:
                tmul = 1
                for num in perm:
                    tmul *= num
                if tmul == result:
                    perms = permutations(perm)
                    for new_perm in perms:
                        if new_perm not in s_tuples:
                            s_tuples.append(tuple(new_perm))
        
        con = Constraint("Box "+ str(i), scope)
        con.add_satisfying_tuples(s_tuples)
        csp_result.add_constraint(con)
    
    return csp_result, variables