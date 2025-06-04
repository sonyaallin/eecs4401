#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from turtle import left
from cspbase import *
import itertools


def get_plus(curr, leftover, num_vars, N):
   if num_vars == 1 and 0 < leftover < N+1:
      return [curr + [leftover]]
   if num_vars == 1:
      return [None]
   tuples = []
   for i in range(1, min(leftover,N+1)):
      returned = get_plus(curr + [i], leftover-i, num_vars-1, N)
      tuples.extend(returned)
   return tuples

def get_times(curr, leftover, num_vars, N):
   if num_vars == 1 and 0 < leftover < N+1:
      return [curr + [leftover]]
   if num_vars == 1:
      return [None]
   tuples = []
   for i in range(1, min(leftover,N+1)):
      if not (leftover % i):
         returned = get_times(curr + [i], leftover // i, num_vars-1, N)
         tuples.extend(returned)
   return tuples


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
   var_grid = []
   N = funpuzz_grid[0][0]
   for r in range(N):
      temp = []
      for c in range(N):
         v = Variable((r+1)*10+(c+1))
         v.add_domain_values(range(1,N+1))
         temp.append(v)
      var_grid.append(temp)

   temp = []
   for v in var_grid:
      temp.extend(v)
   funpuzz_csp = CSP("Binary", temp)

   permutations = list(itertools.permutations(range(1,N+1), 2))
   for p in permutations:
      for r in range(N):
         c = Constraint(f"Row {r+1}", [var_grid[r][p[0]-1], var_grid[r][p[1]-1]])
         c.add_satisfying_tuples(permutations)
         funpuzz_csp.add_constraint(c)
         c = Constraint(f"Col {r+1}", [var_grid[p[0]-1][r], var_grid[p[1]-1][r]])
         c.add_satisfying_tuples(permutations)
         funpuzz_csp.add_constraint(c)
   
   return funpuzz_csp, var_grid


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
   var_grid = []
   N = funpuzz_grid[0][0]
   for r in range(N):
      temp = []
      for c in range(N):
         v = Variable((r+1)*10+(c+1))
         v.add_domain_values(range(1,N+1))
         temp.append(v)
      var_grid.append(temp)

   temp = []
   for v in var_grid:
      temp.extend(v)
   funpuzz_csp = CSP("Binary", temp)

   permutations = list(itertools.permutations(range(1,N+1)))
   for r in range(N):
      c = Constraint(f"Row {r+1}", var_grid[r])
      c.add_satisfying_tuples(permutations)
      funpuzz_csp.add_constraint(c)
   for c in range(N):
      c = Constraint(f"Col {c+1}", [var_grid[r][c] for r in range(N)])
      c.add_satisfying_tuples(permutations)
      funpuzz_csp.add_constraint(c)
   
   return funpuzz_csp, var_grid


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
   N = funpuzz_grid[0][0]
   funpuzz_csp, var_grid = nary_ad_grid(funpuzz_grid)
   for c in funpuzz_grid[1:]:
      if len(c) == 2:
         cons = Constraint(f"Equality", [var_grid[c[0] // 10 - 1][c[0] % 10 - 1]])
         cons.add_satisfying_tuples([[c[1]]])
         funpuzz_csp.add_constraint(cons)
      else:
         vars = [var_grid[i // 10 - 1][i % 10 - 1] for i in c[:-2]]
         operation = c[-1] # (0=’+’, 1=’-’, 2=’/’, 3=’*’)
         target = c[-2]
         # Find all satisfying tuples and add them to a constraint
         # Idea find all possible values assuming the order is constant
         # Once found get all the permutations
         tuples = []
         if operation == 0:
            # If + we know all variables must be less than or equal to target - len(vars)
            for t in get_plus([], target, len(vars), N):
               if t is not None:
                  tuples.extend(itertools.permutations(t))
         elif operation == 1:
            # If - we know all one of the variables must be larger than the target and that all other must be less than that number
            # Moreover, our value will be C1 - sum(C2...CN) = target so C1-target=sum(C2...CN)
            for i in range(1,N+1):
               for t in get_plus([i], i-target, len(vars)-1, N):
                  if t is not None:
                     tuples.extend(itertools.permutations(t))
         elif operation == 2:
            # If / we know one number must be divisible by all others
            # Moreover, our value will be C1 / times(C2...CN) = target so C1-target=times(C2...CN)
            for i in range(1,N+1):
               if not i % target:
                  for t in get_times([i], i // target, len(vars)-1, N):
                     if t is not None:
                        tuples.extend(itertools.permutations(t))
         else:
            # If * we know all numbers must be less than or equal to target
            for t in get_times([], target, len(vars), N):
               if t is not None:
                  tuples.extend(itertools.permutations(t))
         c = Constraint(f"Operation", vars)
         c.add_satisfying_tuples(tuples)
         funpuzz_csp.add_constraint(c)
   return funpuzz_csp, var_grid
