#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
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

   Example list: [[3], [11, 21, 3, 0], [12, 22, 2, 1], [13, 23, 33, 6, 3], [31, 32, 5, 0]]

   Note that this model does not require implementation of cage constraints.
   """
   dim = funpuzz_grid[0][0]
   # variables of problem - for board representation
   variable_array = [[0 for x in range(dim)] for y in range(dim)]
   # variables of problem - for CSP() init function
   CSP_vars = [0 for x in range(dim*dim)]
   domain = [val+1 for val in range(dim)]

   # establish variables
   for row in range(dim):
      for col in range(dim):
         # initialize variable
         name = "V" + str(row+1) + str(col+1)
         var = Variable(name, domain)

         variable_array[row][col] = var
         CSP_vars[row * dim + col] = var

   # init CSP object
   funpuzz_csp = CSP("funpuzz_csp", CSP_vars)

   # establish binary constraints
   for row in range(dim):
      for col in range(dim):
         var1 = variable_array[row][col]

         for c_row in range(row + 1, dim):
            
            # Init constraint on column
            name = str(row+1) + str(col+1) + "c" + str(c_row + 1) + str(col+1)   
            var2 = variable_array[c_row][col]
            con = Constraint(name, [var1, var2])
            
            # values satisfy if x != y
            satisfying = [(x, y) for x in var1.domain() for y in var2.domain() if x != y]

            con.add_satisfying_tuples(satisfying)
            funpuzz_csp.add_constraint(con)
         
         for c_col in range(col + 1, dim):
            
            # Init constraint on row
            name = str(row+1) + str(col+1) + "c" + str(row+1) + str(c_col + 1)
            var2 = variable_array[row][c_col]
            con = Constraint(name, [var1, var2])
            
            # values satisfy if x != y
            satisfying = [(x, y) for x in var1.domain() for y in var2.domain() if x != y]

            con.add_satisfying_tuples(satisfying)
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
   dim = funpuzz_grid[0][0]
   # variables of problem - for grid layout
   variable_array = [[0 for x in range(dim)] for y in range(dim)]
   # variables of problem - for CSP() init
   CSP_vars = [0 for x in range(dim*dim)]
   domain = [val+1 for val in range(dim)]

   # establish variables
   for row in range(dim):
      for col in range(dim):
         # initialize variable
         name = "V" + str(row+1) + str(col+1)
         var = Variable(name, domain)

         variable_array[row][col] = var
         CSP_vars[row * dim + col] = var

   funpuzz_csp = CSP("funpuzz_csp", CSP_vars)

   # possible values for col or row constraints
   satisfying = list(permutations(variable_array[0][0].domain(), dim))

   # establish constraints
   for col in range(dim):
      scope = []
      for c_row in range(dim):
         # Construct the scope of the constraint
         var = variable_array[c_row][col]
         scope.append(var)

      name = "c" + str(col+1)
      con = Constraint(name, scope)
      
      con.add_satisfying_tuples(list(satisfying))
      funpuzz_csp.add_constraint(con)

   for row in range(dim):
      scope = []
      for c_col in range(dim):
         # Construct the scope of the constraint
         var = variable_array[row][c_col]
         scope.append(var)

      name = "r" + str(row+1)
      con = Constraint(name, scope)

      con.add_satisfying_tuples(list(satisfying))
      funpuzz_csp.add_constraint(con)

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

   Example list: [[3], [11, 21, 3, 0], [12, 22, 2, 1], [13, 23, 33, 6, 3], [31, 32, 5, 0]]

   Note that this model does require implementation of cage constraints.
   """
   # variables of problem
   dim = funpuzz_grid[0][0]
   variable_array = [[0 for x in range(dim)] for y in range(dim)]
   CSP_vars = [0 for x in range(dim*dim)]
   domain = [val+1 for val in range(dim)]

   # establish variables
   for row in range(dim):
      for col in range(dim):
         # initialize variable
         name = "V" + str(row+1) + str(col+1)
         var = Variable(name, domain)

         variable_array[row][col] = var
         CSP_vars[row * dim + col] = var

   funpuzz_csp = CSP("funpuzz_csp", CSP_vars)

   # establish binary constraints - same code as binary function
   for row in range(dim):
      for col in range(dim):
         var1 = variable_array[row][col]

         for c_row in range(row + 1, dim):
            
            # Init constraint on column
            name = str(row+1) + str(col+1) + "c" + str(c_row + 1) + str(col+1)   
            var2 = variable_array[c_row][col]
            con = Constraint(name, [var1, var2])
            
            # values satisfy if x != y
            satisfying = [(x, y) for x in var1.domain() for y in var2.domain() if x != y]

            con.add_satisfying_tuples(satisfying)
            funpuzz_csp.add_constraint(con)
         
         for c_col in range(col + 1, dim):
            
            # Init constraint on row
            name = str(row+1) + str(col+1) + "c" + str(row+1) + str(c_col + 1)
            var2 = variable_array[row][c_col]
            con = Constraint(name, [var1, var2])
            
            # values satisfy if x != y
            satisfying = [(x, y) for x in var1.domain() for y in var2.domain() if x != y]

            con.add_satisfying_tuples(satisfying)
            funpuzz_csp.add_constraint(con)


   ### Construct Cage constraints for board ###
   for lst in funpuzz_grid:
      var_lst = []
      satisfying = []

      length = len(lst)
      if length < 2:
         continue
      
      # enforce value on single variable constraint
      if length == 2:
         name = "c" + str(lst[0])

         index = str(lst[0])
         row = int(index[0]) - 1
         col = int(index[1]) - 1

         var = variable_array[row][col]
         con = Constraint(name, [var1])

         satisfying = list(lst[1])

         con.add_satisfying_tuples(satisfying)
         funpuzz_csp.add_constraint(con)
         continue

      # build variable list for multiple variable cage constraint
      for i in range(length - 2):
         index = str(lst[i])
         row = int(index[0]) - 1
         col = int(index[1]) - 1

         # Accumulate variables within the list for constraint
         var_lst.append(variable_array[row][col])
      
      operand = lst[-1]
      target = lst[-2]

      if operand == 0: # + addition operator constraint
         name = "c+" + str([x.name for x in var_lst])

         # Get all combinations of values that add to result
         combinations = list(product(variable_array[0][0].domain(), repeat = length - 2))
         
         for comb in combinations:      
            if sum(comb) == target:
               satisfying.extend(list(permutations(comb, len(comb))))

      elif operand == 1: # - subtraction
         name = "c-" + str([x.name for x in var_lst])
         
         # Get all combinations of values that subtract to result
         combinations = list(product(variable_array[0][0].domain(), repeat = length - 2))
         
         for comb in combinations:
            first_run = True

            for num in comb:
               if first_run:
                  res = num
                  first_run = False
                  continue
               res -= num
            
            if res == target:
               satisfying.extend(list(permutations(comb, len(comb))))

      elif operand == 2: # / division
         name = "c/" + str([x.name for x in var_lst])
         
         # Get all combinations of values that divide to result
         combinations = list(product(variable_array[0][0].domain(), repeat = length - 2))
         
         for comb in combinations:
            first_run = True
            
            for num in comb:
               if first_run:
                  res = num
                  first_run = False
                  continue
               res /= num
            
            if res == target:
               satisfying.extend(list(permutations(comb, len(comb))))
      
      elif operand == 3: # * multiply
         name = "c*" + str([x.name for x in var_lst])
         
         # Get all combinations of values that multiply to result
         combinations = list(product(variable_array[0][0].domain(), repeat = length - 2))
         
         for comb in combinations:      
            res = 1
            for num in comb:
               res *= num
            if res == target:
               satisfying.extend(list(permutations(comb, len(comb))))

      con = Constraint(name, var_lst)
      con.add_satisfying_tuples(satisfying)
      funpuzz_csp.add_constraint(con)
   
   return funpuzz_csp, variable_array
