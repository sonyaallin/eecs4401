#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations, product

OPERATIONS = {0: '+', 1: '-', 2: '/', 3: '*'}

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

   n = funpuzz_grid[0][0]

   funpuzz_csp = CSP(funpuzz)

   variable_array = []
   for i in range(n):
      variable_array.append([])
      for j in range(n):
         var = Variable(str(i+1)+str(j+1), list(range(1,n+1)))
         variable_array[i].append(var)
         funpuzz_csp.add_var(var)

   for i in range(n):
      for j in range(i+1, n):
         for k in range(n):
            funpuzz_csp.add_constraint(Constraint(str(i+1)+str(k+1)+','+str(j+1)+str(k+1), [variable_array[i][k], variable_array[j],[k]])) # The Horizontal
            funpuzz_csp.add_constraint(Constraint(str(k+1)+str(i+1)+','+str(k+1)+str(j+2), [variable_array[k][i], variable_array[k],[j]])) # The Vertical

   satisfying_tuples = [(i,j) for i in range(1,n+1) for j in range(1,n+1) if i != j]

   for con in funpuzz_csp.get_all_cons():
      con.add_satisfying_tuples(satisfying_tuples)

   # Handling Defined Cells
   for cage in funpuzz_grid:
      if len(cage) == 2:
         i = cage[0] // 10
         j = cage[0] % 10
         cons = Constraint("Def "+str(i)+str(j), [variable_array[i-1][j-1]])
         cons.add_satisfying_tuples([cage[1]])
         funpuzz_csp.add_constraint(cons)

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
   n = funpuzz_grid[0][0]

   funpuzz_csp = CSP(funpuzz)

   variable_array = []
   for i in range(n):
      variable_array.append([])
      for j in range(n):
         var = Variable(str(i+1)+str(j+1), list(range(1,n+1)))
         variable_array[i].append(var)
         funpuzz_csp.add_var(var)

   for i in range(n):
      scope_row = []
      scope_col = []
      for j in range(n):
         scope_row.append(variable_array[i][j])
         scope_col.append(variable_array[j][i])
      funpuzz_csp.add_constraint(Constraint("Row "   +str(i+1), scope_row)) # The Horizontal
      funpuzz_csp.add_constraint(Constraint("Column "+str(i+1), scope_col)) # The Vertical

   satisfying_tuples = list(permutations(range(1,n+1)))

   for con in funpuzz_csp.get_all_cons():
      con.add_satisfying_tuples(satisfying_tuples)

   # Handling Defined Cells
   for cage in funpuzz_grid:
      if len(cage) == 2:
         i = cage[0] // 10
         j = cage[0] % 10
         cons = Constraint("Def "+str(i)+str(j), [variable_array[i-1][j-1]])
         cons.add_satisfying_tuples([cage[1]])
         funpuzz_csp.add_constraint(cons)

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
   n = funpuzz_grid[0][0]

   funpuzz_csp = CSP("funpuzz")

   variable_array = []
   for i in range(n):
      variable_array.append([])
      for j in range(n):
         var = Variable(str(i+1)+str(j+1), list(range(1,n+1)))
         variable_array[i].append(var)
         funpuzz_csp.add_var(var)

   for i in range(n):
      scope_row = []
      scope_col = []
      for j in range(n):
         scope_row.append(variable_array[i][j])
         scope_col.append(variable_array[j][i])
      funpuzz_csp.add_constraint(Constraint("Row "   +str(i+1), scope_row)) # The Horizontal
      funpuzz_csp.add_constraint(Constraint("Column "+str(i+1), scope_col)) # The Vertical

   satisfying_tuples = list(permutations(range(1,n+1)))

   for con in funpuzz_csp.get_all_cons():
      con.add_satisfying_tuples(satisfying_tuples)

   # Handling Cages and Defined Cells
   for cage in funpuzz_grid[1:]:
      if len(cage) == 2:
         i = cage[0] // 10
         j = cage[0] % 10
         cons = Constraint("Def "+str(i)+str(j), [variable_array[i-1][j-1]])
         cons.add_satisfying_tuples([cage[1]])
         funpuzz_csp.add_constraint(cons)
      else:
         scope = []
         satisfying_tuples = []
         for cell in cage[:-2]:
            i = cell // 10
            j = cell % 10
            scope.append(variable_array[i-1][j-1])
         total = cage[-2]
         operation = OPERATIONS[cage[-1]]
         num_vars = len(cage) - 2
         for option in product(range(1,n+1),repeat=num_vars):
            eval_string = str(option[0])
            for num in option[1:]:
               eval_string += operation
               eval_string += str(num)
            eval_string += "=="+str(total)
            if eval(eval_string):
               satisfying_tuples += permutations(option) # This causes a lot of repetition, especially in conjunction with the product. But it guarantees order does not matter.

         satisfying_tuples = set(satisfying_tuples)   # By making a set, all the repetition from the previous step is removed
         
         cons = Constraint("Cage "+scope[0].name, scope)
         cons.add_satisfying_tuples(satisfying_tuples)
         funpuzz_csp.add_constraint(cons)         

   return funpuzz_csp, variable_array
