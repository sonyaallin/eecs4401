#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from logging import NullHandler
from tkinter import NS
from cspbase import *
from itertools import permutations, combinations

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
   funpuzz_csp = CSP("binary_grid_funpuzz")
   grid_array_size = len(funpuzz_grid)
   grid_size = 0
   variable_array = [[grid_array_size]]

   if grid_array_size > 0:
      grid_size = funpuzz_grid[0][0]
   else:
      return None
   
   init_domain = gen_domain(grid_size)

   for x in range(1, grid_size+1):
      lst = []
      for y in range(1, grid_size+1):
         lst.append(Variable(str((x*10) + y), init_domain))
      variable_array.append(lst)
      for var in variable_array[x]:
         funpuzz_csp.add_var(var)
         
      
   
   sat_tuples = gen_sat_tuples(grid_size)
   #init_domain = gen_domain(grid_size)

   #curr_cell = (None, None)
   #max_cell = (grid_size, grid_size)
   

   
   funpuzz_csp = build_binary_row_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array)
   funpuzz_csp = build_binary_col_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array)
   variable_array.pop(0)
   return funpuzz_csp, variable_array


def build_binary_row_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array):
   curr_var = None
   
   for x in range(1, grid_size+1):
      #print("x: "+str(x))
      #curr_var = variable_array[x][0]
      #print("curr_var: "+str(curr_var))
      constraints_to_build = list(combinations(variable_array[x], 2))
      #print("constraints_to_build: "+str(constraints_to_build))
      
      for (var1, var2) in constraints_to_build:
         new_cons = Constraint(str((var1, var2)), [var1, var2])
         for sat_tuple_array in sat_tuples:
            new_cons.add_satisfying_tuples(sat_tuple_array)
         funpuzz_csp.add_constraint(new_cons)
      
   return funpuzz_csp

def build_binary_col_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array):

   
   curr_var = None
   for col in range(1, grid_size+1):
      other_col_vars = []
      curr_var = variable_array[1][col-1]
      #print("curr_col_var:"+str(curr_var))
      for row in range(2, grid_size+1):
         other_var = variable_array[row][col-1]
         other_col_vars.append(other_var)
         #print("other_col_var:"+str(other_var))
         new_cons =  Constraint( str((curr_var, other_var)), [curr_var, other_var])
         for sat_tuple_array in sat_tuples:
            new_cons.add_satisfying_tuples(sat_tuple_array)
         funpuzz_csp.add_constraint(new_cons)
      constraints_to_build = list(combinations(other_col_vars, 2))
      for (var1, var2) in constraints_to_build:
            new_cons = Constraint(str((var1, var2)), [var1, var2])
            for sat_tuple_array in sat_tuples:
               new_cons.add_satisfying_tuples(sat_tuple_array)
            funpuzz_csp.add_constraint(new_cons)
   return funpuzz_csp
   

def gen_sat_tuples(n):
   sat_tuples = []
   i = 1
   while i <= n:
      sat_tuples.append([])
      for other_val in range(1, n+1):
         if other_val != i:
            sat_tuples[i-1].append((i, other_val))
      i += 1
   return sat_tuples

def gen_domain(n):
   return [x for x in range(1, n+1)]

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
   funpuzz_csp = CSP("nary_grid_funpuzz")
   grid_array_size = len(funpuzz_grid)
   grid_size = 0
   variable_array = [[grid_array_size]]
   
   

   if grid_array_size > 0:
      grid_size = funpuzz_grid[0][0]
   else:
      return None
   
   init_domain = gen_domain(grid_size)

   for x in range(1, grid_size+1):
      lst = []
      for y in range(1, grid_size+1):
         lst.append(Variable(str((x*10) + y), init_domain))
      variable_array.append(lst)
      for var in variable_array[x]:
         funpuzz_csp.add_var(var)
   
   
   sat_tuples = gen_nary_tuples(grid_size)
   #init_domain = gen_domain(grid_size)

   #curr_cell = (None, None)
   #max_cell = (grid_size, grid_size)
   funpuzz_csp = build_nary_row_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array)
   funpuzz_csp = build_nary_col_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array)
   variable_array.pop(0)
   return funpuzz_csp, variable_array

def gen_nary_tuples(n):
    poss_values = [x for x in range(1, n+1)]
    #print("poss_values:", poss_values)
    perm = list(permutations(poss_values))
    return perm

def build_nary_row_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array):
   curr_row = []
   for row in range(1, grid_size+1):
      curr_row = variable_array[row]
      new_cons = Constraint("row: "+ str(row), curr_row)
      new_cons.add_satisfying_tuples(sat_tuples)
   return funpuzz_csp

def build_nary_col_constraints(funpuzz_csp, grid_size, sat_tuples, variable_array):
   for col in range(1, grid_size+1):
      curr_col = []
      for row in range(1, grid_size+1):
         curr_col.append(variable_array[row][col-1])
      new_cons = Constraint("col: "+ str(col), curr_col)
      new_cons.add_satisfying_tuples(sat_tuples)
   return funpuzz_csp


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
   funpuzz_csp = CSP("binary_cage_funpuzz")
   grid_array_size = len(funpuzz_grid)
   grid_size = 0
   variable_array = [[grid_array_size]]
   
   
   
   if grid_array_size > 0:
      grid_size = funpuzz_grid[0][0]
   else:
      return None
   init_domain = gen_domain(grid_size)
   for x in range(1, grid_size+1):
      lst = []
      for y in range(1, grid_size+1):
         lst.append(Variable(str((x*10) + y), init_domain))
      variable_array.append(lst)
      for var in variable_array[x]:
         funpuzz_csp.add_var(var)
   
   binary_sat_tuples = gen_sat_tuples(grid_size)
   #init_domain = gen_domain(grid_size)

   #curr_cell = (None, None)
   #max_cell = (grid_size, grid_size)
   funpuzz_csp = build_binary_row_constraints(funpuzz_csp, grid_size, binary_sat_tuples, variable_array)
   #for cons in funpuzz_csp.get_all_cons():
   #   print(str(cons.name)+" scope:"+str(cons.get_scope())+" sat_tuples:"+str(cons.sat_tuples)+"\n")

   funpuzz_csp = build_binary_col_constraints(funpuzz_csp, grid_size, binary_sat_tuples, variable_array)
   #for cons in funpuzz_csp.get_all_cons():
   #   print(str(cons.name)+" scope:"+str(cons.get_scope())+" sat_tuples:"+str(cons.sat_tuples)+"\n")
   i = 1
   while i < grid_array_size:
      curr_cage = funpuzz_grid[i]
      curr_cage_length = len(curr_cage)
      #print("curr_cage: ", curr_cage)
      #print("curr_cage_length: ", curr_cage_length)
      
      if curr_cage_length == 2:
         funpuzz_csp = cage_enforce_helper(funpuzz_csp, curr_cage, variable_array)
         

      elif curr_cage_length > 2:
         target = curr_cage[curr_cage_length - 2]
         #print("target: ", target)
         operation = curr_cage[curr_cage_length - 1]
         #print("operation: ", operation)
         cage_variables = []
         for index in range(0, curr_cage_length - 2):
            cage_variables.append(curr_cage[index])
         
         comb = list(combinations(init_domain, len(cage_variables)))
         funpuzz_csp = cage_constraint_helper(funpuzz_csp, target, operation, cage_variables, grid_size, variable_array, comb)

      i +=1
   
   variable_array.pop(0)
   return funpuzz_csp, variable_array

def cage_enforce_helper(funpuzz_csp, curr_cage, variable_array):
   target = curr_cage[1]
   row = curr_cage[0] // 10
   col = curr_cage[0] % 10

   curr_var = variable_array[row][col-1]
   new_cons = Constraint(str((row*10)+col), [curr_var])
   new_cons.add_satisfying_tuples((target))
   funpuzz_csp.add_constraint(new_cons)
   return funpuzz_csp

def cage_constraint_helper(funpuzz_csp, target, operation, cage_variables, grid_size, variable_array, comb):
   #n = len(cage_variables)
   #poss_values = [x for x in range(1, grid_size+1)]
   #perm = list(permutations(poss_values, n))
   #comb = list(combinations(poss_values, n)) #TRY WITH INIT DOMAIN
   cage = []

   for var in cage_variables:
      cage.append(variable_array[var//10][(var%10)-1])

   new_constraint = Constraint(str(cage_variables) , cage)
   if operation == 0:
      #print(comb)
      for tuple in comb:
         #print(tuple)
         if sum(tuple) == target:
            sub_perm = list(permutations(tuple))
            #print(sub_perm)
            new_constraint.add_satisfying_tuples(sub_perm)
   elif operation == 1:
      for tuple in comb:
         sub_perm = list(permutations(tuple))
         valid = False
         i = 0
         while not valid and i < len(sub_perm):
            if len(sub_perm[i]) == 1 and sub_perm[i][0] == target:
               valid = True
            elif sub_perm[i][0] - sum(sub_perm[i][1:]) == target:
               valid = True
            i += 1
         if valid:
            new_constraint.add_satisfying_tuples(sub_perm) 
   elif operation == 2:
      for tuple in comb:
         sub_perm = list(permutations(tuple))
         if tuple_div_valid(sub_perm, target):
            new_constraint.add_satisfying_tuples(sub_perm)
   elif operation == 3:
      for tuple in comb:
         if tuple_product(tuple) == target:
            sub_perm = list(permutations(tuple))
            new_constraint.add_satisfying_tuples(sub_perm)
   
   funpuzz_csp.add_constraint(new_constraint)

   return funpuzz_csp


def tuple_product(tuple) :
     
    # Multiply elements one by one
    product = 1
    for value in tuple:
         product *= value
    return product

def tuple_div_valid(perm, target) :
    for p in perm:
        if div_recursive_helper(p) == target:
            return True
        
def div_recursive_helper(tuple):
    n = len(tuple)
    if n == 1:
        return tuple[0]
    elif n == 2:
        return tuple[0]/tuple[1]
    else:
        return div_recursive_helper(tuple[:(n - 1)])/tuple[n - 1]

if __name__ == '__main__':
   test_csp, var_array = funpuzz_csp_model([[4], [11, 21, 6, 3], [12, 13, 3, 0], [14, 24, 3, 1], [22, 23, 7, 0], [31, 32, 2, 2], [33, 43, 3, 1],
           [34, 44, 6, 3], [41, 42, 7, 0]])
   all_cons = test_csp.get_all_cons()
   for cons in all_cons:
      print(str(cons.name)+" scope:"+str(cons.get_scope())+" sat_tuples:"+str(cons.sat_tuples)+"\n")
   print(str(var_array))
   test_csp.print_all()
