#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only 
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary 
      all-different constraints for both the row and column constraints. 

'''
from typing import NewType
from cspbase import *
import itertools

def create_neq_con(isRow,cons,row,i,j,var1,var2):
    '''Helper function that creates a binary inequality constraint constraint'''
    con = None
    if isRow:
        con = Constraint("C(row{}:{}&{})".format(row,i,j),[var1, var2])
    else:
        con = Constraint("C(col{}:{}&{})".format(row,i,j),[var1, var2])
    sat_tuples = []
    for t in itertools.product(var1.domain(), var2.domain()):
        if t[0] != t[1]:
            sat_tuples.append(t)
    con.add_satisfying_tuples(sat_tuples)
    cons.append(con)

def create_ineq_con(sign,cons,var1,var2):
    '''Helper function that creates an > or < constraint'''
    sat_tuples = []
    if sign == '.':
        return
    elif sign == '<':
        con = Constraint("C({}<{})".format(var1, var2),[var1, var2])
        for t in itertools.product(var1.domain(), var2.domain()):
            if t[0] < t[1]:
                sat_tuples.append(t)
    elif sign == '>':
        con = Constraint("C({}>{})".format(var1, var2),[var1, var2])
        for t in itertools.product(var1.domain(), var2.domain()):
            if t[0] > t[1]:
                sat_tuples.append(t)
    
    con.add_satisfying_tuples(sat_tuples)
    cons.append(con)

def futoshiki_csp_model_1(futo_grid):
    n = len(futo_grid)

    dom = list(range(1, n+1))

    # Create variables
    vars = []
    varlist = []
    for row in range(1,n+1):
        varlist.append([])
        for col in range(1,n+1):
            var = None
            if futo_grid[row-1][(col-1)*2] == 0:
                var = Variable('num({},{})'.format(row,col), dom)
            else:
                var = Variable('num({},{})'.format(row,col), [futo_grid[row-1][(col-1)*2]])
                var.assign(futo_grid[row-1][(col-1)*2])
            vars.append(var)
            varlist[row-1].append(var)

    cons = []
    # Create row and col constraints
    for row in range(1,n+1):
        for i in range(1,n):
            for j in range(i+1,n+1):
                create_neq_con(True,cons,row,i,j,vars[(row-1)*n+i-1], vars[(row-1)*n+j-1])
    for col in range(1,n+1):
        for i in range(1,n):
            for j in range(i+1,n+1):
                create_neq_con(False,cons,col,i,j,vars[(i-1)*n+col-1], vars[(j-1)*n+col-1])
    
    # Create inequality constraints
    for row in range(1,n+1):
        for col in range(1,n):
            create_ineq_con(futo_grid[row-1][(col-1)*2+1], cons, vars[(row-1)*n+col-1], vars[(row-1)*n+col])

    csp = CSP("Futo {}x{}".format(n,n), vars)
    for c in cons:
        csp.add_constraint(c)
    return csp, varlist


def create_alldiff_con(isRow,cons,num,n,vars):
    '''Helper function that creates an n-ary all diff constraint'''
    con = None
    scope = None
    if isRow:
        scope = [vars[(num-1)*n+x-1] for x in range(1,n+1)]
        con = Constraint("C(row{})".format(num),scope)
    else:
        scope = [vars[(x-1)*n+num-1] for x in range(1,n+1)]
        con = Constraint("C(col{})".format(num),scope)
    sat_tuples = []
    
    recurseGen([],sat_tuples,n,1)

    con.add_satisfying_tuples(sat_tuples)
    cons.append(con)

def recurseGen(tup,sat_tuples,n,i):
    '''Helper function to create_alldiff_con() that creates the sat_tuples for an all-diff constraint with n variables with values 1-n'''
    for val in range(1,n+1):
        for elem in tup:
            if elem == val: # Go to the next val
                break 
        else: # This only occurs if the above loop didn't break
            tup.append(val)
            
            if i == n:
                sat_tuples.append(tuple(tup))
            else:
                recurseGen(tup,sat_tuples,n,i+1)
            tup.pop()

def futoshiki_csp_model_2(futo_grid):
    n = len(futo_grid)

    dom = list(range(1, n+1))

    # Create variables
    vars = []
    varlist = []
    for row in range(1,n+1):
        varlist.append([])
        for col in range(1,n+1):
            var = None
            if futo_grid[row-1][(col-1)*2] == 0:
                var = Variable('num({},{})'.format(row,col), dom)
            else:
                var = Variable('num({},{})'.format(row,col), [futo_grid[row-1][(col-1)*2]])
                var.assign(futo_grid[row-1][(col-1)*2])
            vars.append(var)
            varlist[row-1].append(var)

    cons = []
    # Create row and col constraints
    for k in range(1,n+1):
        create_alldiff_con(True,cons,k,n,vars)
        create_alldiff_con(False,cons,k,n,vars)
    
    # Create inequality constraints
    for row in range(1,n+1):
        for col in range(1,n):
            create_ineq_con(futo_grid[row-1][(col-1)*2+1], cons, vars[(row-1)*n+col-1], vars[(row-1)*n+col])

    csp = CSP("Futo {}x{}".format(n,n), vars)
    for c in cons:
        csp.add_constraint(c)
    return csp, varlist
   
