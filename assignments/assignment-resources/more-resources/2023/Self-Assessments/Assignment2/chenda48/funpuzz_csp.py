#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations

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
    fp_csp = CSP(' a name')
    n = funpuzz_grid[0][0]
    vars = [[] for i in range(n)]
    for var in vars:
       for i in range(n):
          var.append('')
         
    "Add variables to the CSP and variable_array"
    for cage_i in range(1, len(funpuzz_grid)):
      cage = funpuzz_grid[cage_i]
      if len(cage) == 2:
         coord = cage[0]
         val = cage[1]
         new_var = Variable(str(coord), [val])
      else:
         for coord in cage[:-2]:
            new_var = Variable(str(coord), [i for i in range(1, n+1)])
            x = int(str(coord)[0]) - 1
            y = int(str(coord)[1]) - 1
            vars[x][y] = new_var
            fp_csp.add_var(new_var)
    
    "Generate all binary constraint values"
    con_values = []
    for val1 in range(n):
         for val2 in range(val1+1, n):
            con_values.append((val1+1, val2+1))
            con_values.append((val2+1, val1+1))

    "Add constraints to the CSP"
    for r in range(n): # By row
      for c in range(n-1):
         for c2 in range(c+1, n):
            scope = [vars[r][c], vars[r][c2]]
            new_constraint = Constraint('r' + str(r) + 'c' + str(c) + str(c2), scope)
            new_constraint.add_satisfying_tuples(con_values)
            fp_csp.add_constraint(new_constraint)

    for c in range(n): # By column
      for r in range(n-1):
         for r2 in range(r+1, n):
            scope = [vars[r][c], vars[r2][c]]
            new_constraint = Constraint('c' + str(c) + 'r' + str(r) + str(r2), scope)
            new_constraint.add_satisfying_tuples(con_values)
            fp_csp.add_constraint(new_constraint)
    
    return fp_csp, vars


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
    fp_csp = CSP(' a name')
    n = funpuzz_grid[0][0]
    vars = [[] for i in range(n)]
    for var in vars:
       for i in range(n):
          var.append('')
         
    "Add variables to the CSP and variable_array"
    for cage_i in range(1, len(funpuzz_grid)):
      cage = funpuzz_grid[cage_i]
      if len(cage) == 2:
         coord = cage[0]
         val = cage[1]
         new_var = Variable(str(coord), [val])
      else:
         for coord in cage[:-2]:
            new_var = Variable(str(coord), [i for i in range(1, n+1)])
            x = int(str(coord)[0]) - 1
            y = int(str(coord)[1]) - 1
            vars[x][y] = new_var
            fp_csp.add_var(new_var)

    "Generate all row/column constraint permutations"
    con_values = [i for i in range(1,n+1)]
    permute_con = [con for con in permutations(con_values)]
    
    
    "Add constraints to the CSP"
    for r in range(n): # By row
      s = []
      for c in range(n):
         s.append(vars[r][c])
      
      new_constraint = Constraint('r'+str(r), s)
      new_constraint.add_satisfying_tuples(permute_con)
      fp_csp.add_constraint(new_constraint)

    for c in range(n): # By column
      s = []
      for r in range(n):
         s.append(vars[r][c])
      
      new_constraint = Constraint('c' + str(c), s)
      new_constraint.add_satisfying_tuples(permute_con)
      fp_csp.add_constraint(new_constraint)
    
    return fp_csp, vars


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
    fp_csp, vars = binary_ne_grid(funpuzz_grid) 
   #  fp_csp, vars = nary_ad_grid(funpuzz_grid) 
    n = funpuzz_grid[0][0]

    for grid_i in range(1, len(funpuzz_grid)):
      grid = funpuzz_grid[grid_i]
      if len(grid) != 2: # Create  constraint
         var_l = []
         goal = grid[-2]
         op = grid[-1]
         con_n = []
         s = str(op) + '-'
         for var_i in range(len(grid)-2):
            var = grid[var_i]
            r = int(str(var)[0]) - 1
            c = int(str(var)[1]) - 1
            var_l.append(vars[r][c])
            s = s + str(r+1) + str(c+1)
            con_n.append(str(r) + str(c))
         
         new_gconstraint = Constraint(s, var_l)
         
         con_values = find_solutions(goal, op, len(grid)-2, [i for i in range(1,n+1)], con_n)
         # print(con_values)
         
         # print(var_l)
         new_gconstraint.add_satisfying_tuples(con_values)
         fp_csp.add_constraint(new_gconstraint)

    return fp_csp, vars

def find_solutions(goal, op, n_var, domain, con):
   sol = []

   if len(con) > 2:
      seen_r = []
      seen_c = []
      for i in range(len(con)):
         var1 = con[i]
         r = int(str(var1)[0]) - 1
         c = int(str(var1)[1]) - 1
         if r not in seen_r:
            seen_r.append(r)
         if c not in seen_c:
            seen_c.append(c)
      
      repeats = min(len(seen_r), len(seen_c))     
      domain = domain * repeats

   all_p = permutations(domain, n_var)

   if op == 0: #add
      for p in all_p:
         if sum(p) == goal:
            sol.append(p)
   elif op == 1: #subtract
      for p in all_p:
         res = p[0]
         for p_i in range(1,len(p)):
            res = res - p[p_i]
         if res == goal:
            sol = sol + [o for o in permutations(p)]
   elif op == 2: #divide
      for p in all_p:
         res = p[0]
         for p_i in range(1,len(p)):
            res = res/p[p_i]
         if res == goal:
            sol = sol + [o for o in permutations(p)]
   else: #multiply
      for p in all_p:
         product = p[0]
         for p_i in range(1,len(p)):
            product = product * p[p_i]
         if product == goal:
            sol.append(p)

   return sol