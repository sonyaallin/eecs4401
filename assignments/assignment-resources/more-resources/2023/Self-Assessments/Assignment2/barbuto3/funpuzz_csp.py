#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools

ADD=0
SUB=1
DIV=2
MUL=3

def sat_binary_ne_tuples(dim):
    res=[]
    for d1 in range(1, dim+1):
        for d2 in range(1, dim+1):
            if d1!=d2:
                res.append((d1, d2))
    return res

def sat_nary_alldiff_tuples(dim):
    # generate all perms of length dim
    return list(itertools.permutations(range(1, dim+1)))

def apply_op(t1, t2, operation):
    if operation==ADD: return t1+t2
    elif operation==SUB: return t1-t2
    elif operation==DIV: return t1/t2
    elif operation==MUL: return t1*t2
    return t1==t2

def sat_cage_cons_tuples(size, dim, operation, target):
    res = []

    # generate all permutations/configurations of tuples with specified size with possible range == dimenstion
    perms = list(itertools.permutations(range(1, dim+1), size))
    
    # save perms that satisfy: i_1 op i_2 op ... op i_k == target
    for p in perms:
        t=p[0]
        i=1
        while i<size:
            t = apply_op(t, p[i], operation)
            i+=1
        if t==target:
            res.append(p)
    return res

def cell_str_to_var(cell, variable_array):
    name = str(cell)
    row,col = int(name[0])-1, int(name[1])-1 # by convention, we are only considering n = 3->9

    # find Variable object corresponding to cell
    return variable_array[row][col]

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
    csp = CSP("binary_ne_grid")
    dim = funpuzz_grid[0][0]

    variable_array = []
    # populate csp and variable_array grid with list of variable objects
    for r in range(dim):
        vrow = []
        for c in range(dim):
            v = Variable(f"({r+1},{c+1})", range(1, dim+1))
            csp.add_var(v)
            vrow.append(v)
        variable_array.append(vrow)

    # populate csp with row and column binary constraint objects
    tuples = sat_binary_ne_tuples(dim)  # all constraints start with the same satisifying tuples
    for r in range(dim):
        for c in range(dim):
            # get all combinations of column constraints between a given cell[r,c] and cells under it 
            # Note: start from row k=r+1 since constraints for cells above row r+1 have already been made with cell[r,c]
            v1 = variable_array[r][c]
            for k in range(r+1, dim):
                v2 = variable_array[k][c]

                # get satisfying tuples for constraint, add constraint to csp
                con = Constraint(f"({r+1},{c+1})_({k+1},{c+1})", set([v1, v2]))
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
            
            # do the same for row constraints: col k=c+1 since constrains for cells to the left have already been made with cell[r,c]
            for k in range(c+1, dim):
                v2 = variable_array[r][k]

                # get satisfying tuples for constraint, add constraint to csp
                con = Constraint(f"({r+1},{c+1})_({r+1},{k+1})", set([v1, v2]))
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)

    return csp, variable_array


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
    csp = CSP("n-ary_alldiff_grid")
    dim = funpuzz_grid[0][0]

    variable_array = []
    # populate csp and variable_array grid with list of variable objects
    for r in range(dim):
        vrow = []
        for c in range(dim):
            v = Variable(f"({r+1},{c+1})", range(1, dim+1))
            csp.add_var(v)
            vrow.append(v)
        variable_array.append(vrow)

    # n-ary constraints: one constraint for each row and each col, each containing variables in that row/col as the scope
    tuples = sat_nary_alldiff_tuples(dim) # all constraints start with the same satisifying tuples
    # tuples = permutations(list(range(1, dim+1)))  # all constraints start with the same satisifying tuples
    for i in range(dim):
        # row i
        row_con = Constraint(f"row{i+1}", variable_array[i])
        row_con.add_satisfying_tuples(tuples)
        csp.add_constraint(row_con)

        # col i
        col_con = Constraint(f"col{i+1}", [r[i] for r in variable_array])
        col_con.add_satisfying_tuples(tuples)
        csp.add_constraint(col_con)

    return csp, variable_array

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
    csp = CSP("funpuzz_csp_model")
    dim = funpuzz_grid[0][0]

    variable_array = []
    # populate csp and variable_array grid with list of variable objects
    for r in range(dim):
        vrow = []
        for c in range(dim):
            v = Variable(f"({r+1},{c+1})", range(1, dim+1))
            csp.add_var(v)
            vrow.append(v)
        variable_array.append(vrow)

    # populate csp with row and column binary constraint objects
    tuples = sat_binary_ne_tuples(dim)  # all constraints start with the same satisifying tuples
    for r in range(dim):
        for c in range(dim):
            # get all combinations of column constraints between a given cell[r,c] and cells under it 
            # Note: start from row k=r+1 since constraints for cells above row r+1 have already been made with cell[r,c]
            v1 = variable_array[r][c]
            for k in range(r+1, dim):
                v2 = variable_array[k][c]

                # get satisfying tuples for constraint, add constraint to csp
                con = Constraint(f"({r+1},{c+1})_({k+1},{c+1})", set([v1, v2]))
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)
            
            # do the same for row constraints: col k=c+1 since constrains for cells to the left have already been made with cell[r,c]
            for k in range(c+1, dim):
                v2 = variable_array[r][k]

                # get satisfying tuples for constraint, add constraint to csp
                con = Constraint(f"({r+1},{c+1})_({r+1},{k+1})", set([v1, v2]))
                con.add_satisfying_tuples(tuples)
                csp.add_constraint(con)

    # populate csp with cage constraints (each will have length == # cells in the cage)
    # for a given cage: cage has only 2 elements => first is the cell, second is the target num, operation is EQ
    #                   cage has n >= 3 elements => first n-2 are cells, the n-1th is the target, the nth is the operation
    cages = funpuzz_grid[1:]
    cage_num=1
    for c in cages:
        operation=None
        target=None
        if len(c)==2: # [cell, target]
            target=c[-1]
            cage=c[:-1]
        elif len(c)>2: # [cells..., target, operation]
            operation=c[-1]
            target=c[-2]
            cage=c[:-2]
        else: continue # skip invalid cages


        # map cell strings to their corresponding Variable objects, create constraint between them
        cage_scope = list(map((lambda x: cell_str_to_var(x, variable_array)), cage))
        cage_tuples = sat_cage_cons_tuples(len(cage_scope), dim, operation, target)

        con = Constraint(f"cage{cage_num}", cage_scope)
        con.add_satisfying_tuples(cage_tuples)
        csp.add_constraint(con)
        cage_num+=1
    
    return csp, variable_array


