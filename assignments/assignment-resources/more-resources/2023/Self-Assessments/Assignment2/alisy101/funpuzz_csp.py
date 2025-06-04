#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools

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
   size = funpuzz_grid[0][0]
   variables = [[0 for i in range(size)] for i in range(size)]
   domain=[i for i in range (1, size+1)]
   cspf = CSP(' binary_ne_grid')

   for i in range(size):
      for j in range(size):
         variables[i][j] = Variable(str(i+1) + str(j+1),  domain)
         cspf.add_var(variables[i][j])
   
   satisfy_tups = list(itertools.permutations(range(1, size+1), 2))

   for k in range(size):
      for i in range(size):
         for j in range(i+1, size):
            row_cons = Constraint('row '+str(k+1), (variables[k][i], variables[k][j]))
            row_cons.add_satisfying_tuples(satisfy_tups)
            cspf.add_constraint(row_cons)
            col_cons = Constraint('column '+str(k+1), (variables[i][k], variables[j][k]))
            col_cons.add_satisfying_tuples(satisfy_tups)
            cspf.add_constraint(col_cons)

   return cspf, variables


         
   
   
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
   size = funpuzz_grid[0][0]
   variables = [[0 for i in range(size)] for i in range(size)]
   rows = [[] for i in range(size)]
   columns = [[] for i in range(size)]
   domain=[i for i in range (1, size+1)]
   cspf = CSP(' nary_ad_grid')

   for i in range(size):
      for j in range(size):
         variables[i][j] = Variable(str(i+1) + str(j+1),  domain)
         rows[i].append(variables[i][j])
         columns[j].append(variables[i][j])
         cspf.add_var(variables[i][j])


   satisfy_tups = list(itertools.permutations(range(1, size+1), size))
   for k in range(size):
      row_cons = Constraint('row '+str(k+1), rows[k])
      row_cons.add_satisfying_tuples(satisfy_tups)
      cspf.add_constraint(row_cons)
      col_cons = Constraint('column '+str(k+1), columns[k])
      col_cons.add_satisfying_tuples(satisfy_tups)
      cspf.add_constraint(col_cons)
   return cspf, variables


def prod(lst):
   val = 1
   for item in lst:
      val *= item
   return val


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
   size = funpuzz_grid[0][0]
   domain=[i for i in range (1, size+1)]
   cspf, variables = binary_ne_grid(funpuzz_grid)
   for i in range(1, len(funpuzz_grid)):
      scope = [variables[int(str(i)[0])-1][int(str(i)[1])-1] for i in funpuzz_grid[i][:len(funpuzz_grid[i])-2]]
      cage_cons = Constraint('Cage '+str(i), scope)
      lst = []
      for satisfy_tups in list(itertools.product(domain, repeat=len(funpuzz_grid[i])-2)):
         val = None
         if funpuzz_grid[i][-1] == 0:
            val = sum(satisfy_tups)
         elif funpuzz_grid[i][-1] == 3:
            val = prod(satisfy_tups)
         else:
            permlst = list(itertools.permutations(satisfy_tups))
            for tuples in permlst:
               if funpuzz_grid[i][-1] == 1:
                  val = tuples[0] - sum(tuples[1:])
               elif funpuzz_grid[i][-1] == 2:
                  val = tuples[0] / prod(tuples[1:])
               if val == funpuzz_grid[i][-2]:
                  break
         if val == funpuzz_grid[i][-2]:
            lst.append(satisfy_tups)
      cage_cons.add_satisfying_tuples(lst)      
      cspf.add_constraint(cage_cons)
   return cspf, variables



