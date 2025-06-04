#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import *

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
   dims = funpuzz_grid[0][0] # The dimensions of the grid
   domain = [i for i in range(1, dims + 1)] # The intial domain for all variables
   variable_array = []
   satisfying_tuples = list(permutations(domain, 2)) # the valid variable assignments for all the constraints
   funbuzz_csp = CSP("FunPuzz")
   count = 1 # used for constraint name


   # Create the variable array for the csp problem
   for row in range(dims):
      variable_array_row = []
      for col in range(dims):
         var = Variable("V" + str(row) + str(col), domain)
         variable_array_row.append(var)
         funbuzz_csp.add_var(var)

      variable_array.append(variable_array_row)
     
      #Generate all binary row constraints
      row_variables_binary_combination = list(combinations(variable_array_row, 2))
      for element in row_variables_binary_combination:
         cons = Constraint("C"+ str(count), element)   
         cons.add_satisfying_tuples(satisfying_tuples)
         funbuzz_csp.add_constraint(cons)
         count += 1
      
   #Generate all binary column constraints. Note: we already created variable array
   for col_index in range(dims):
      variables_in_col = []
      for row_index in range(dims):
         var = variable_array[row_index][col_index]
         variables_in_col.append(var)
      
      # We have all the variables at column 'col_index'
      col_variables_binary_combination = list(combinations(variables_in_col, 2))
      for element in col_variables_binary_combination:
         cons = Constraint("C" + str(count), element)   
         cons.add_satisfying_tuples(satisfying_tuples)
         funbuzz_csp.add_constraint(cons)
         count += 1


   return funbuzz_csp, variable_array



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

   dims = funpuzz_grid[0][0] # The dimensions of the grid
   domain = [i for i in range(1, dims + 1)] # The intial domain for all variables
   variable_array = []
   satisfying_values_assignments = list(permutations(domain, dims))
   funbuzz_csp = CSP("FunPuzz")
   count = 1 # used for constraint name

   # Create the variable array for the csp problem
   for row in range(dims):
      variable_array_row = []
      for col in range(dims):
         var = Variable("V" + str(row) + str(col), domain)
         variable_array_row.append(var)
         funbuzz_csp.add_var(var)

      variable_array.append(variable_array_row)
     
      # Generate n-ary row constraint
      # the order of variables inside constraint will be left to right or top to bottom?
      cons = Constraint("C" + str(count), variable_array_row)   
      cons.add_satisfying_tuples(satisfying_values_assignments)
      funbuzz_csp.add_constraint(cons)  
      count += 1  
  
   for col_index in range(dims):
      variables_in_col = []
      for row_index in range(dims):
         var = variable_array[row_index][col_index]
         variables_in_col.append(var)
      
      # We have all the variables at column 'col_index'
      cons = Constraint("C" + str(count), variables_in_col)
      cons.add_satisfying_tuples(satisfying_values_assignments)
      funbuzz_csp.add_constraint(cons)
      count += 1

   return funbuzz_csp, variable_array



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
   funbuzz_csp, variable_array = nary_ad_grid(funpuzz_grid)
   dims = funpuzz_grid[0][0] # The dimensions of the grid
   domain = [i for i in range(1, dims + 1)] # The intial domain for all variables
   count = dims * 2 + 1 # we already generate dims * 2 constraints from the call above

   # Now we have to generate the cage constraints

   for i in range(1, len(funpuzz_grid)):
      cage = funpuzz_grid[i]
      variables_coordinates = cage[0: -2] if len(cage) > 2 else cage[0]
      variables_in_cage_cons = []
      target = funpuzz_grid[i][-2] if len(cage) > 2 else cage[1]
      operand = funpuzz_grid[i][-1] if len(cage) > 2 else None
      cage_cons = None

      # Need to populate the scope for the cage constraint
      for cell_name in variables_coordinates:
         row = int(str(cell_name)[0]) - 1
         col = int(str(cell_name)[1]) - 1
         var = variable_array[row][col]
         variables_in_cage_cons.append(var)
      
      cage_cons = Constraint("C" + str(count), variables_in_cage_cons)
      funbuzz_csp.add_constraint(cage_cons)
      count += 1
     
      # now need to populate the constraint with the satisfying tuples
      if operand == None:
         # we know there will be only 1 variable in this constraint
         # we also know the target, so we assign that variable to this value
         cage_cons.add_satisfying_tuples(((target)))
         variables_in_cage_cons[0].assign(target)

      else:
         # we need to filter out permuations which don't result in the target with the specified operand
         all_combs = list(combinations_with_replacement(domain, len(variables_in_cage_cons)))
         cage_cons_sat_variable_assignments = []

         for comb in all_combs:
            # check if the permuation satisfies constraint, if so add it to the 
            if operand == 0:
               all_perms = list(permutations(comb, len(comb)))
               for perm in all_perms:
                  if sum(perm) == target:
                     cage_cons_sat_variable_assignments.extend(all_perms)
                     break
            
            
            elif operand == 1:
               all_perms = list(permutations(comb, len(comb)))
               for perm in all_perms:
                  diff = perm[0]
                  for number in perm[1:]:
                     diff -= number
                  if diff == target:
                     cage_cons_sat_variable_assignments.extend(all_perms)
                     break
            
            elif operand == 2:
               all_perms = list(permutations(comb, len(comb)))
               for perm in all_perms:
                  quotient = perm[0]
                  for number in perm[1:]:
                     quotient /= number
                  if quotient == target:
                     cage_cons_sat_variable_assignments.extend(all_perms)
                     break
            
            elif operand == 3:
               all_perms = list(permutations(comb, len(comb)))
               for perm in all_perms:
                  product = perm[0]
                  for number in perm[1:]:
                     product *= number
                  if product == target:
                     cage_cons_sat_variable_assignments.extend(all_perms)
                     break
         
         cage_cons.add_satisfying_tuples(cage_cons_sat_variable_assignments)
   
   return funbuzz_csp, variable_array  


