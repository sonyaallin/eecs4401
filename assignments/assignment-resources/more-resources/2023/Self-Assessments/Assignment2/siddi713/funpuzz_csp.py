#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations, product

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
  dim = funpuzz_grid[0][0]
  domain = list(range(1, dim+1))

  csp_variable_array = []
  return_variable_array = []
  for row in range(dim):
      return_variable_array.append([])
      for col in range(dim):
        return_variable_array[row].append(Variable(f'Cell({row+1}, {col+1})', domain))
        csp_variable_array.append(return_variable_array[row][col])
  
  funpuzz_csp = CSP(f"Binary_NE_Grid_FunPuzz_Size({dim})", csp_variable_array)
  perms = list(permutations(domain, 2))
  
  for row in range(dim):
    for col in range(dim):
      var = return_variable_array[row][col]          
      for i in range(dim):
        if i != row:
          temp_var = return_variable_array[i][col]
          con = Constraint(f'{var.name} != {temp_var.name}', [var, temp_var])
          con.add_satisfying_tuples(perms)
          funpuzz_csp.add_constraint(con)
        if i != col:
          temp_var = return_variable_array[row][i]
          con = Constraint(f'{var.name} != {temp_var.name}', [var, temp_var])
          con.add_satisfying_tuples(perms)
          funpuzz_csp.add_constraint(con)
  
  return funpuzz_csp, return_variable_array


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
  domain = list(range(1, dim+1))

  csp_variable_array = []
  return_variable_array = []
  for row in range(dim):
    return_variable_array.append([])
    for col in range(dim):
      return_variable_array[row].append(Variable(f'Cell({row+1}, {col+1})', domain))
      csp_variable_array.append(return_variable_array[row][col])
  
  funpuzz_csp = CSP(f"Nary_ad_Grid_FunPuzz_Size({dim})", csp_variable_array)
  perms = list(permutations(domain, dim))

  for i in range(dim):
    row_var_list = []
    col_var_list = []
    for j in range(dim):
      row_var_list.append(return_variable_array[i][j])
      col_var_list.append(return_variable_array[j][i])
    
    row_con = Constraint(f'Row {i+1}', row_var_list)
    row_con.add_satisfying_tuples(perms)
    funpuzz_csp.add_constraint(row_con)

    col_con = Constraint(f'Col{i+1}', col_var_list)
    col_con.add_satisfying_tuples(perms)
    funpuzz_csp.add_constraint(col_con)

  return funpuzz_csp, return_variable_array

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
  dim = funpuzz_grid[0][0]
  domain = list(range(1, dim+1))
  funpuzz_csp, variable_array = nary_ad_grid(funpuzz_grid)

  for cage in funpuzz_grid[1:]:
    
    cells = cage[:1]
    perm_len = 1
    target = cage[-1]
    operation = -1
    
    if len(cage) > 2:
      cells = cage[:-2]
      perm_len = len(cells)
      target = cage[-2]
      operation = cage[-1]
      
    sat_perms = []
    perms = list(product(domain, repeat=perm_len))
    for perm in perms:
      if is_constraint_satisfied(perm, operation, target):
        sat_perms.append(perm)
        
    cage_var_list = []
    for cell in cells:
      row = (cell // 10) - 1
      col = (cell % 10) - 1
      cage_var_list.append(variable_array[row][col])
    
    cage_con = Constraint(f'Cage({cells})', cage_var_list)
    cage_con.add_satisfying_tuples(sat_perms)
    funpuzz_csp.add_constraint(cage_con)    
      
  return funpuzz_csp, variable_array

def is_constraint_satisfied(values, operation, target):
  """Returns True if the constraint is satisfied by the assignment, and False otherwise.
  """
  total = values[0]
  if (operation == 0):
    for i in values[1:]:
      total += i
    return total == target
  elif (operation == 1):
    perms = list(permutations(values, len(values)))
    for perm in perms:
      total = perm[0]
      for i in perm[1:]:
        total -= i
      if (total == target):
        return True
    return False
  elif (operation == 2):
    perms = list(permutations(values, len(values)))
    for perm in perms:
      total = perm[0]
      for i in perm[1:]:
        total //= i
      if (total == target):
        return True
    return False
  elif (operation == 3):
    for i in values[1:]:
      total *= i
  return total == target