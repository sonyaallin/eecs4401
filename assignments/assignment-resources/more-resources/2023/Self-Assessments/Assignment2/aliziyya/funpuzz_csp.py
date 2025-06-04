#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools, string

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
   dimensions = funpuzz_grid[0][0]
   variable_array = []
   variables = []
   temp_row = []
   count = dimensions
   init_count = 1
   # create the variable array
   for row,col in itertools.product(string.ascii_lowercase[:dimensions], repeat=2):
      v = None
      if init_count <= dimensions:
         v = Variable(row+col, [init_count])
         v.assign(init_count)
         init_count += 1
      else:
         v = Variable(row+col, list(range(1, dimensions+1)))
      temp_row.append(v)
      variables.append(v)
      count -= 1
      if count == 0:
         variable_array.append(temp_row)
         count = dimensions
         temp_row = []

   # find all constraint pairs 
   con_pairs = []
   for i in range(len(variable_array)):
      for j in range(len(variable_array)):
         if i == 0:
            con_pairs.append((variable_array[i][j], None))
         for n in range(j+1, len(variable_array)):
            con_pairs.append((variable_array[i][j], variable_array[i][n]))
            con_pairs.append((variable_array[j][i], variable_array[n][i]))
   
   # inialize csp
   funpuzz_csp = CSP('Binary NE', vars=variables)

   # create constraints for each pair
   for var1, var2 in con_pairs:
      con = None
      if var2 is None:
         con = Constraint(str(var1), [var1])
      else:
         con = Constraint(str(var1) + '<->' + str(var2), [var1, var2])
      # set the satisfying tuples for the constraint (variables must not be equal)
      tups = []
      for i in range(1, dimensions+1):
         for j in range(1, dimensions+1):
            if var1.domain_size() == 1:
                  tups.append((j,))
            elif i != j:
               tups.append((i, j))
      con.add_satisfying_tuples(tups)
      # add constraint to the csp
      funpuzz_csp.add_constraint(con)

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
   pass


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
   return binary_ne_grid(funpuzz_grid)


