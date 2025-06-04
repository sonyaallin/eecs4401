#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import numpy as np
from itertools import permutations
from itertools import product

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
   size = funpuzz_grid[0][0] + 1

   variable_array = []
   for i in range(1, size):
      row_var = []
      for j in range(1, size):
         var = Variable(str(i)+str(j), [i for i in range(1, size)])
         row_var.append(var)
      variable_array.append(row_var)

   variable_array = np.array(variable_array)
   
   funpuzz_csp = CSP("binary_ne_grid")
   for i in range(0, size-1):
      for j in range(0, size-1):
         funpuzz_csp.add_var(variable_array[i, j])

   cons = []
   for i in range(1, size):
      for j in range(1, size):
         if i != j:
            cons.append((i, j))

   for i in range(0, size-1):
      for j in range(0, size-1):
         var1 = variable_array[i, j]
         for var2 in variable_array[i, j+1:]:
            scope = [var1, var2]
            cur_cons = Constraint(var1.name+var2.name, scope)
            cur_cons.add_satisfying_tuples(cons)
            funpuzz_csp.add_constraint(cur_cons)
               
         for var2 in variable_array[i+1:, j]:
            scope = [var1, var2]
            cur_cons = Constraint(var1.name+var2.name, scope)
            cur_cons.add_satisfying_tuples(cons)
            funpuzz_csp.add_constraint(cur_cons)
   
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
   size = funpuzz_grid[0][0] + 1

   variable_array = []
   for i in range(1, size):
      row_var = []
      for j in range(1, size):
         var = Variable(str(i)+str(j), [i for i in range(1, size)])
         row_var.append(var)
      variable_array.append(row_var)

   variable_array = np.array(variable_array)
   
   funpuzz_csp = CSP("nary_ad_grid")
   for i in range(0, size-1):
      for j in range(0, size-1):
         funpuzz_csp.add_var(variable_array[i, j])

   cons = [i for i in range(1, size)]

   for row in variable_array:
      cur_cons = Constraint("row", row)
      cur_cons.add_satisfying_tuples(permutations(cons))
      funpuzz_csp.add_constraint(cur_cons)
   
   for col in variable_array.T:
      cur_cons = Constraint("col", col)
      cur_cons.add_satisfying_tuples(permutations(cons))
      funpuzz_csp.add_constraint(cur_cons)
   
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

   def fval(values, result_op):
      result, op = result_op
      if op == 0:
         return np.sum(values) == result
      elif op == 1:
         for i in range(len(values)):
            lst = [result]+list(values[:i])+list(values[i+1:])
            if fval(lst, [values[i], 0]):
               return True
         return False
      elif op == 2:
         for i in range(len(values)):
            lst = [result]+list(values[:i])+list(values[i+1:])
            if fval(lst, [values[i], 3]):
               return True
         return False
      else:
         total = values[0]
         for val in values[1:]:
            total *= val
         return total == result

   funpuzz_csp, variable_array = binary_ne_grid(funpuzz_grid)
   size = funpuzz_grid[0][0] + 1

   for cage_cons in funpuzz_grid[1:]:
      if len(cage_cons) == 2:
         end = 1
      else:
         end = len(cage_cons) - 2
      
      scope = []
      for var_name in cage_cons[:end]:
         var_row = int(str(var_name)[0]) - 1
         var_col = int(str(var_name)[1]) - 1

         scope.append(variable_array[var_row, var_col])
      
      cur_cons = Constraint("cage", scope)
      if len(cage_cons) == 2:
         cur_cons.add_satisfying_tuples([(cage_cons[1])])

      else:
         cons = [i for i in range(1, size)]
         all_sat = [c for c in product(cons, repeat=end) if fval(c, cage_cons[end:])]
         cur_cons.add_satisfying_tuples(all_sat)
      
      funpuzz_csp.add_constraint(cur_cons)
   
   return funpuzz_csp, variable_array
