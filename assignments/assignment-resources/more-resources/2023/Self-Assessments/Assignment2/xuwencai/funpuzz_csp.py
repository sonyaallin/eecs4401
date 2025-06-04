#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

import itertools

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
   # initialze variable list
   n = funpuzz_grid[0][0]
   variable_lst = []
   variables = []

   for i in range(1, n+1):
      rows = []
      for j in range(1, n+1):
         v_name = i * 10 + j
         v = Variable(v_name, [i for i in range(1, n + 1)])
         rows.append(v)
         variables.append(v)
      variable_lst.append(rows)
   
   # initialize satisfy tuples
   satisfy_tuples = set()

   for i in range(1, n+1):
      for j in range(1, n+1):
         if i != j:
            satisfy_tuples.add( (i, j) )
  
   # initialize row constraints

   csp = CSP('binary_ne', variables)

   for i in range(0, n):

      for v1 in range(0, n):
         for v2 in range(v1+1, n):

            var1 = variable_lst[i][v1]
            var2 = variable_lst[i][v2]
            constraint1 = Constraint('', [var1, var2])
            constraint1.add_satisfying_tuples(satisfy_tuples)
            csp.add_constraint(constraint1)

            var3 = variable_lst[v1][i]
            var4 = variable_lst[v2][i]
            constraint2 = Constraint('', [var3, var4])
            constraint2.add_satisfying_tuples(satisfy_tuples)
            csp.add_constraint(constraint2)
   
   return csp, variable_lst


def nary_ad_grid(funpuzz_grid):
   """
    A model of a funpuzz grid (without cage constraints) built using only n-ary all-different
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
   variable_lst = []
   variables = []

   for i in range(1, n+1):
      rows = []
      for j in range(1, n+1):
         v_name = i * 10 + j
         v = Variable(v_name, [i for i in range(1, n + 1)])
         rows.append(v)
         variables.append(v)
      variable_lst.append(rows)
   
   # satisfy tuples
   csp = CSP('n-ary', variables)
   satisfy_tuples = set(itertools.permutations([i for i in range(1, n+1)]))
    
   for i in range(n):
      row_const = Constraint('', variable_lst[i])

      col_const = Constraint('', [row[i] for row in variable_lst])

      row_const.add_satisfying_tuples(satisfy_tuples)
      col_const.add_satisfying_tuples(satisfy_tuples)

      csp.add_constraint(row_const)
      csp.add_constraint(col_const)
    
   return csp, variable_lst


def cell_to_position(cell_num):
   
   row = cell_num // 10 - 1
   col = cell_num % 10 - 1

   return row, col


def permute(nums):
   result = []
   backtrack(nums, [], result)
   return result
        
def backtrack(nums, path, result):
   if not nums:
      result.append(path)
   for i in range(len(nums)):
      backtrack(nums[:i] + nums[i+1:], path + [nums[i]], result)


def funpuzz_csp_model(funpuzz_grid):
   """
    A model built using your choice of (1) binary binary not-equal, or (2) n-ary all-different
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

   csp, variable_lst = binary_ne_grid(funpuzz_grid)

   dim = funpuzz_grid[0][0]
    
   for i in range(1, len(funpuzz_grid)):

      cage = funpuzz_grid[i]
       
      if len(cage) == 2:
         row, col = cell_to_position(cage[0])
         constraint = Constraint('', [variable_lst[row][col]])
         constraint.add_satisfying_tuples([cage[1]])
         csp.add_constraint(constraint)
         continue
      
      tuples = list(itertools.combinations_with_replacement([i for i in range(1, dim + 1)], len(cage) - 2))

      # [[1,2,3], [1,3,4], [1,4,5]] if n = 5 and cage is 3
         
      # init variables
      variables = []
      for cell_num in cage[0: -2]:
         row, col = cell_to_position(cell_num)
         variables.append(variable_lst[row][col])
         
         # init constraints
      constraint = Constraint('', variables)
         
      satisfy_tuples = []

      for tuple in tuples:

         if cage[-1] == 0 and sum(tuple) == cage[-2]:  # sum
            
            satisfy_tuples = satisfy_tuples + permute(tuple)

         elif cage[-1] == 3:  # multiply

            multiply = 1

            for num in tuple:
               multiply *= num
            
            if multiply == cage[-2]:
               satisfy_tuples = satisfy_tuples + permute(tuple)
      
         elif cage[-1] == 2:
            
            for i in range(len(tuple)):
               total = tuple[i]

               for j in range(i-1, -1, -1):
                  total = total / tuple[j]
               
               for j in range(i+1, len(tuple), 1):
                  total = total / tuple[j]
               
               if total == cage[-2]:
                  satisfy_tuples = satisfy_tuples + permute(tuple)
                  break
      
         elif cage[-1] == 1:

            for i in range(len(tuple)):
               total = tuple[i]

               for j in range(i-1, -1, -1):
                  total = total - tuple[j]
               
               for j in range(i+1, len(tuple), 1):
                  total = total - tuple[j]
               
               if total == cage[-2]:
                  satisfy_tuples = satisfy_tuples + permute(tuple)
                  break

      constraint.add_satisfying_tuples(satisfy_tuples)

      csp.add_constraint(constraint)
    
   return csp, variable_lst

