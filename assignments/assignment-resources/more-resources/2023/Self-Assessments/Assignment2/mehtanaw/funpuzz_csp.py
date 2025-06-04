#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations, product

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
    # get size of grid and domain of variables
    N = funpuzz_grid[0][0]
    domain = [x for x in range(1,N+1)]
    # create CSP
    csp = CSP('Funpuzz')

    # create variable for each cell on the grid
    variables = []
    for i in domain:
       row = []
       for j in domain:
          v = Variable('V'+str(i)+str(j), domain)
          # add variable to the CSP
          csp.add_var(v)
          row.append(v)
       variables.append(row)
    
    # create list of satisfying tuples for binary not equal constraint
    sat_tuples = []
    for i in domain:
       for j in domain:
          if i != j:
             sat_tuples.append((i, j))

    # create and add all constraints 
    for row_col in domain:
      for v1 in domain:
         for v2 in range(v1+1, N+1):
            # create constraint on variables which lie on this row
            c1 = Constraint('C'+str(row_col)+str(v1)+','+str(row_col)+str(v2), [variables[row_col-1][v1-1], variables[row_col-1][v2-1]])
            # add satisfying tuples to constraint and add constraint to CSP
            c1.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(c1)

            # create constraint on the transposed variables which lie on the opposite/transposed column
            c2 = Constraint('C'+str(v1)+str(row_col)+','+str(v2)+str(row_col), [variables[v1-1][row_col-1], variables[v2-1][row_col-1]])
            # add satisfying tuples to constraint and add constraint to CSP
            c2.add_satisfying_tuples(sat_tuples)
            csp.add_constraint(c2)

    return csp, variables


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
    # get size of grid and domain of variables
    N = funpuzz_grid[0][0]
    domain = [x for x in range(1,N+1)]
    # create CSP
    csp = CSP('Funpuzz')

    # create variable for each cell on the grid
    variables = []
    for i in domain:
       row = []
       for j in domain:
          v = Variable('V'+str(i)+str(j), domain)
          # add variable to the CSP
          csp.add_var(v)
          row.append(v)
       variables.append(row)
    
    # create list of satisfying tuples for n-ary all diff constraint
    # take all permutations of the domian with N elements
    sat_tuples = list(permutations(domain, N))
    
    # create and add all constraints 
    for row_col in domain:
      # add constraint on row
      c1 = Constraint('C_row'+str(row_col), variables[row_col-1])
      # add satisfying tuples to constraint and add constraint to CSP
      c1.add_satisfying_tuples(sat_tuples)
      csp.add_constraint(c1)

      # add constraint on opposite/transposed column
      c2 = Constraint('C_col'+str(row_col), [variables[x][row_col-1] for x in range(N)])
      # add satisfying tuples to constraint and add constraint to CSP
      c2.add_satisfying_tuples(sat_tuples)
      csp.add_constraint(c2)

    return csp, variables


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
    # get size of grid and domain of variables
    N = funpuzz_grid[0][0]
    domain = [x for x in range(1,N+1)]
    # create basic CSP model with binary constraints for rows and columns(without cage constraints)
    csp, variables = binary_ne_grid(funpuzz_grid)
    
    # create and add all cage constraints
    for cage_num in range(1, len(funpuzz_grid)):
       # store list for cage
       cage = funpuzz_grid[cage_num]
       # if this cage has only two elements(one cell and its value)
       if len(cage) == 2:
          cell = str(cage[0])
          i = int(cell[0])
          j = int(cell[1])
          # get satisfying tuple(which is the one value given) 
          sat_tuples = [(cage[1])]
          # create constraint, add satisfying tuple and add constraint to CSP
          c = Constraint('C_Cage'+str(cage_num), [variables[i-1][j-1]])
          c.add_satisfying_tuples(sat_tuples)
          csp.add_constraint(c)
       # if this cage contains multiple cells
       else:
          # get operation and final value
          operation = cage[-1]
          value = cage[-2]

          # get all variables and number of variables
          vars = []
          counter = 0
          for cell_num in range(len(cage)-2):
             cell = str(cage[cell_num])
             i = int(cell[0])
             j = int(cell[1])
             vars.append(variables[i-1][j-1])
             counter += 1
          
          # create list of potential satisfying tuples
          # use cross product between domain of variables(number of domains is number of variables)
          mayb_tuples = list(product(domain, repeat=counter))
          sat_tuples = []
          
          # add potential tuple if it satisfies the constraint
          for tuple in mayb_tuples:
             curr_val = tuple[0]

             for index in range(1, len(tuple)):
                if operation == 0:
                   curr_val += tuple[index]
                elif operation == 1:
                   curr_val -= tuple[index]
                elif operation == 2:
                   curr_val = curr_val/tuple[index]
                elif operation == 3:
                   curr_val = curr_val*tuple[index]
             
             # add all permutations of tuple as order of values on the grid does 
             # not matter for satisfying cage constraints
             if curr_val == value:
                cons_tuples = list(permutations(tuple, len(tuple)))
                sat_tuples.extend(cons_tuples)    

          # create constriant, add satisfying tuples and add constraint to CSP
          c = Constraint('C_Cage'+str(cage_num), vars)
          c.add_satisfying_tuples(sat_tuples)
          csp.add_constraint(c)

    return csp, variables