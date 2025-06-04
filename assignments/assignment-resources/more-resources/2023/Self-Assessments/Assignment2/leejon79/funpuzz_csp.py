#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

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
   size = funpuzz_grid[0][0]
   domain = []
   for val in range(1, size + 1):
      domain.append(val)

   variable_array = []
   funpuzz_csp = CSP("funpuzz")

   for i in range(0, size):
      temp_array = []
      for j in range(0, size):
         new_var = Variable(str(i + 1) + str(j + 1), domain.copy())
         temp_array.append(new_var)
         funpuzz_csp.add_var(new_var)
      variable_array.append(temp_array)

   for i in range(0, size):
      for j in range(0, size):
         for m in range(i + 1, size):
            sat_tups = []
            new_constraint_name = variable_array[i][j].name + " " +  variable_array[m][j].name + " binary NE"
            new_constraint = Constraint(new_constraint_name, [variable_array[i][j], variable_array[m][j]])
            for val1 in domain:
               for val2 in domain:
                  if val1 != val2:
                     sat_tups.append((val1, val2))
            new_constraint.add_satisfying_tuples(sat_tups)
            funpuzz_csp.add_constraint(new_constraint)
         for n in range(j + 1, size):
            sat_tups = []
            new_constraint_name = variable_array[i][j].name + " " +  variable_array[i][n].name + " binary NE"
            new_constraint = Constraint(new_constraint_name, [variable_array[i][j], variable_array[i][n]])
            for val1 in domain:
               for val2 in domain:
                  if val1 != val2:
                     sat_tups.append((val1, val2))
            new_constraint.add_satisfying_tuples(sat_tups)
            funpuzz_csp.add_constraint(new_constraint)
   
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
   size = funpuzz_grid[0][0]
   domain = []
   for val in range(1, size + 1):
      domain.append(val)

   variable_array = []
   funpuzz_csp = CSP("funpuzz")

   for i in range(0, size):
      temp_array = []
      for j in range(0, size):
         new_var = Variable(str(i + 1) + str(j + 1), domain.copy())
         temp_array.append(new_var)
         funpuzz_csp.add_var(new_var)
      variable_array.append(temp_array)

   sat_tups = tuple(all_diff([], domain.copy()))

   for i in range(0, size):
      new_row_constraint_name = "Row " + str(i) + " nary"
      new_column_constraint_name = "Column " + str(i) + " nary"
      row_scope = []
      column_scope = []
      for j in range(0, size):
         row_scope.append(variable_array[i][j])
         column_scope.append(variable_array[j][i])
      new_row_constraint = Constraint(new_row_constraint_name, row_scope)
      new_row_constraint.add_satisfying_tuples(sat_tups)
      funpuzz_csp.add_constraint(new_row_constraint)
      new_column_constraint = Constraint(new_column_constraint_name, column_scope)
      new_column_constraint.add_satisfying_tuples(sat_tups)
      funpuzz_csp.add_constraint(new_column_constraint)
   
   return funpuzz_csp, variable_array

#Helper function to create lists that have different values at every index
def all_diff(lst, available_vals):
   return_lsts = []
   if available_vals == []:
      return [lst]
   for var in available_vals:
      tmp_lst = lst.copy()
      tmp_lst.append(var)
      avail_vals_copy = available_vals.copy()
      avail_vals_copy.remove(var)
      tmp = all_diff(tmp_lst, avail_vals_copy)
      for part in tmp:
         return_lsts.append(part)
   return return_lsts

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
   domain = []
   for val in range(1, size + 1):
      domain.append(val)

   funpuzz_csp, variable_array = nary_ad_grid(funpuzz_grid)

   for i in range(1, len(funpuzz_grid)):
      operation = funpuzz_grid[i][-1]
      goal_val = funpuzz_grid[i][-2]
      curr_vars = funpuzz_grid[i][0:-2]
      new_constraint_name = ""

      all_poss_values = all_values([], size, 0, len(curr_vars))

      scope = []
      for var in curr_vars:
         scope.append(variable_array[int(str(var)[0]) - 1][int(str(var)[1]) - 1])

      sat_tuples = []

      if operation == 0:
         new_constraint_name = "Plus constraint, Goal:" + str(goal_val)
         for values in all_poss_values:
            total = 0
            for value in values:
               total += value
            if total == goal_val:
               sat_tuples.append(values)

      elif operation == 1:
         new_constraint_name = "Minus constraint, Goal:" + str(goal_val)
         all_orders = all_diff([], domain.copy()[0:len(curr_vars)])
         for order in all_orders:
            total = 0
            for values in all_poss_values:
               total = values[order[0] - 1]
               for i in order[1:]:
                  total -= values[i - 1]
               if total == goal_val:
                  sat_tuples.append(values)
      elif operation == 2:
         new_constraint_name = "Divide constraint, Goal:" + str(goal_val)
         all_orders = all_diff([], domain.copy()[0:len(curr_vars)])
         for order in all_orders:
            total = 0
            for values in all_poss_values:
               total = values[order[0] - 1]
               for i in order[1:]:
                  total = total / values[i - 1]
               if total == float(goal_val):
                  sat_tuples.append(values)
      else:
         new_constraint_name = "Times constraint, Goal:" + str(goal_val)
         for values in all_poss_values:
            total = values[0]
            for value in values[1:]:
               total = total * value
            if total == goal_val:
               sat_tuples.append(values)

      new_constraint = Constraint(new_constraint_name, scope)
      new_constraint.add_satisfying_tuples(tuple(sat_tuples))
      funpuzz_csp.add_constraint(new_constraint)

   return funpuzz_csp, variable_array

#Gets all possible combinations of all allowed values
def all_values(lst, max_val, curr_size, max_size):
   return_lst = []
   if curr_size == max_size:
      return [lst]
   for i in range(1, max_val + 1):
      tmp_lst = lst.copy()
      tmp_lst.append(i)
      new_size = curr_size + 1
      tmp = all_values(tmp_lst, max_val, new_size, max_size)
      for part in tmp:
         return_lst.append(part)
   return return_lst