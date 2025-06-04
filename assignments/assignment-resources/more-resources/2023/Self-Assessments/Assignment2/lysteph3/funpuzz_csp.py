#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from math import perm
from cspbase import *
import itertools as it

def satifying_pairs(i,j):
   return [(k,v) for k in i.cur_domain() for v in j.cur_domain() if k != v]

def index_translation(number):
   return ((number // 10) - 1, (number % 10) - 1)
   
def function(operation, lst , target): 
   if (operation == 0): # adding
      result = lst[0]
      for i in range(1, len(lst)):
         result += lst[i]
      return result == target
   elif (operation == 1): # subtracting
      result = lst[0]
      for i in range(1, len(lst)):
         result -= lst[i]
      return result == target
   elif (operation == 2): # dividing
      result = lst[0]
      for i in range(1, len(lst)):
         result /= lst[i]
      return result == target
   elif (operation == 3): # multiplying
      result = lst[0]
      for i in range(1, len(lst)):
         result *= lst[i]
      return result == target
   else: 
      print("ERROR")
      return None
   
   
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
   
   # parameters
   size = funpuzz_grid[0][0]
   variable_array = [[Variable("{}{}".format(j,i), range(1,size+1)) for i in range(size)] for j in range (size)]
   csp = CSP("binary_ne_grid", list(it.chain.from_iterable(variable_array)))

   # indices we need to iterate through
   for v in range(size):
      for k in range(size):
         for w in range(size):
            
            # Do nothing
            if k == w or v == w: continue
            
            # Extract a column
            constraint = Constraint("column", [variable_array[v][k],variable_array[w][k]])
            constraint.add_satisfying_tuples(satifying_pairs(variable_array[v][k],variable_array[w][k]))
            csp.add_constraint(constraint)
            
            # Extract a row
            constraint = Constraint("row", [variable_array[v][k],variable_array[v][w]])
            constraint.add_satisfying_tuples(satifying_pairs(variable_array[v][k],variable_array[v][w]))
            csp.add_constraint(constraint)
            
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
   
   # parameters
   size = funpuzz_grid[0][0]
   variable_array = [[Variable("{}{}".format(j,i), range(1,size+1)) for i in range(size)] for j in range (size)]
   csp = CSP("nary_ad_grid", list(it.chain.from_iterable(variable_array)))
   
   # n-ary relations
   perms = tuple(itertools.permutations(range(1,size+1)))
   
   for index in range(size):
      
      # Extract a column
      constraint = Constraint("column", [variable_array[index][row] for row in range(size)])
      constraint.add_satisfying_tuples(perms)
      csp.add_constraint(constraint)
      
      # Extract a row
      constraint = Constraint("row", [variable_array[column][index] for column in range(size)])
      constraint.add_satisfying_tuples(perms)
      csp.add_constraint(constraint)
      
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
   
   # Initialize the funpuzz grid   
   csp, variables = binary_ne_grid(funpuzz_grid)
   
   # Remove the size and start constraint count
   cages = funpuzz_grid[1:]
   count = 0
   
   for cage in cages:
      equation_variables=cage[:-2]
      operation=cage[-1]
      target=cage[-2]
      
      # When there are parameters for the constraint
      if len(cages) > 2: 
         cage_domain = [variables[index_translation(variable)[0]][index_translation(variable)[1]].cur_domain() for variable in equation_variables]
         cage_variables = [variables[index_translation(variable)[0]][index_translation(variable)[1]] for variable in equation_variables]
         constraint = Constraint("Cage contraint #: {}".format(count), cage_variables)
         cartesian_products = itertools.product(*cage_domain)
         for product in cartesian_products:
            # Only process cartesian multiples of size cage_variables, don't accept not complete 
            if len(list(product)) == len(cage_variables):
               if function(operation, product, target):
                  # Add all permuations of the n-ary constraint
                  perms = itertools.permutations(product)
                  constraint.add_satisfying_tuples(perms)
         csp.add_constraint(constraint)
      # When there are no parameters for the constraint
      else:
         indices = index_translation(target)
         constraint = Constraint("equality:{}={}".format(indices[0],indices[1]), [variables[indices[0]][indices[1]]])
         constraint.add_satisfying_tuples((operation,))
         csp.add_constraint(constraint)
      count += 1
   return csp, variables


