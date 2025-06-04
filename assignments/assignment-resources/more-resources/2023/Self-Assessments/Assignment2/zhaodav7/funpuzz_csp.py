#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
import itertools

def all_diff_pairs(var1, var2):
   '''helper to return all unique pairings of different values'''
   pairs = []
   for i in var1.cur_domain():
      for j in var2.cur_domain():
         if (i != j):
            pairs.append((i,j))
   return pairs


def operate(op, lst):
   '''helper to operate repeatedly'''
   ret = lst[0]
   for num in lst[1:]:
      if op==0:
         ret+=num
      elif op==1:
         ret-=num
      elif op==2:
         ret/=num
      elif op==3:
         ret*=num
      else:
         return None
   return ret


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
   default_domain=range(1,n+1)
   vars = [[Variable(str((j+1)*10+(i+1)), default_domain[:]) for i in range(n)] for j in range(n)]
   csp = CSP("binary_ne_grid", [item for sublist in vars for item in sublist])

   for i in range(n):
      for j in range(n):
         # set the contraints for each var
         for k in range(n):
            # binary constraints in tuples of two
            c1 = Constraint("row", [vars[i][j],vars[i][k]])
            c1.add_satisfying_tuples(all_diff_pairs(vars[i][j],vars[i][k]))
            if k!=j:
               csp.add_constraint(c1)
            c2 = Constraint("col", [vars[i][j],vars[k][j]])
            c2.add_satisfying_tuples(all_diff_pairs(vars[i][j],vars[k][j]))
            if k!=i:
               csp.add_constraint(c2)
   return csp, vars


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
   default_domain=range(1,n+1)
   vars = [[Variable(str((j+1)*10+(i+1)), default_domain[:]) for i in range(n)] for j in range(n)]
   csp = CSP("nary_ad_grid", [item for sublist in vars for item in sublist])
   # single instance of permutation calculation to reference off of to reduce computation
   permutations = tuple(itertools.permutations(range(1,n+1)))
   for i in range(n):
      # nary constraints in tuples representing entire valid rows/cols
      c1 = Constraint("row", [vars[i][k] for k in range(n)])
      c1.add_satisfying_tuples(permutations)
      csp.add_constraint(c1)
      c2 = Constraint("col", [vars[k][i] for k in range(n)])
      c2.add_satisfying_tuples(permutations)
      csp.add_constraint(c2)
   return csp, vars


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
   rest_cons = funpuzz_grid[1:]
   cages=len(rest_cons)
   # using binary, because it is faster
   csp, vars = binary_ne_grid(funpuzz_grid)
   # adding cages constraints
   for c in rest_cons:
      result=c[-2]
      operation=c[-1]
      cage_vars=c[:-2]
      if not cage_vars:
         # two element sepcial case: result->var, operation->target
         c = Constraint("unary_=", [vars[(result//10)-1][(result%10)-1]])
         c.add_satisfying_tuples(tuple([operation]))
         csp.add_constraint(c)
      else:
         # cage operation
         cage = [vars[(v//10)-1][(v%10)-1].cur_domain() for v in cage_vars]
         if operation==0:
            # +
            name = "cage_-"
         elif operation==1:
            # -
            name = "cage_-"
         elif operation==2:
            # /
            name = "cage_/"
         elif operation==3:
            # *
            name = "cage_*"
         else:
            continue
         c = Constraint(name, [vars[(v//10)-1][(v%10)-1] for v in cage_vars])
         for product in itertools.product(*cage):
            if operate(operation, product) == result:
               if operation==1 or operation==2:
                  # - and / requires all permutations to be valid
                  c.add_satisfying_tuples(itertools.permutations(product))
               else:
                  c.add_satisfying_tuples([product])
         csp.add_constraint(c)
   return csp, vars


