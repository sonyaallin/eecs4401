# Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from aem import con
from appscript import k
from cspbase import *
import itertools

def binary_ne_grid(funpuzz_grid):
   """
    A model of a funpuzz grid (without cage constraints) built using only binary all-different
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
   var = []
   csp_obj = CSP("funpuzz")
   for i in range(funpuzz_grid[0][0]):
      row = []
      for j in range(funpuzz_grid[0][0]):
         domain = [1,2,3,4,5,6,7,8,9]
         to_add = Variable("variable_array[{}][{}]".format(i, j), domain)
         csp_obj.add_var(to_add)
         row.append(to_add)
      var.append(row)
   
   row_num = 0
   index_combinator = [x for x in range(0, funpuzz_grid[0][0])]
   index_combinations = list(itertools.combinations(index_combinator, 2))
   for var_row in var:
      for index_tup in index_combinations:
         cons = Constraint("AllDiff_row[{}]".format(row_num), [var_row[index_tup[0]], var_row[index_tup[1]]])
         sub_var = [var_row[index_tup[0]], var_row[index_tup[1]]]
         domains = []
         for variable in sub_var:
            domains.append(variable.domain())
         tuples = []
         for t in itertools.product(*domains):
            if len(t) == len(set(t)):
               tuples.append(t)
         cons.add_satisfying_tuples(tuples)
         csp_obj.add_constraint(cons)
      row_num += 1

   for i in range(len(var)):
      temp = []
      for j in range(len(var[i])):
         temp.append(var[j][i])
      for index_tup in index_combinations:
         cons = Constraint("AllDiff_column[{}]".format(i), [var_row[index_tup[0]], var_row[index_tup[1]]])
         sub_var = [var_row[index_tup[0]], var_row[index_tup[1]]]
         domains = []
         for variable in sub_var:
            domains.append(variable.domain())
         tuples = []
         for t in itertools.product(*domains):
            if len(t) == len(set(t)):
               tuples.append(t)
         cons.add_satisfying_tuples(tuples)
         csp_obj.add_constraint(cons)


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
   var = []
   csp_obj = CSP("funpuzz")
   for i in range(funpuzz_grid[0][0]):
      row = []
      for j in range(funpuzz_grid[0][0]):
         domain = [1,2,3,4,5,6,7,8,9]
         to_add = Variable("variable_array[{}][{}]".format(i, j), domain)
         csp_obj.add_var(to_add)
         row.append(to_add)
      var.append(row)
   
   row_num = 0
   for var_row in var:
      cons = Constraint("AllDiff_row[{}]".format(row_num), var_row)
      domains = []
      for variable in var_row:
         domains.append(variable.domain())
      tuples = []
      for t in itertools.product(*domains):
         if len(t) == len(set(t)):
            tuples.append(t)
      cons.add_satisfying_tuples(tuples)
      csp_obj.add_constraint(cons)
      row_num += 1

   for i in range(len(var)):
      temp = []
      for j in range(len(var[i])):
         temp.append(var[j][i])
      cons = Constraint("AllDiff_column[{}]".format(i), temp)
      domains = []
      for variable in temp:
         domains.append(variable.domain())
      tuples = []
      for t in itertools.product(*domains):
         if len(t) == len(set(t)):
            tuples.append(t)
      cons.add_satisfying_tuples(tuples)
      csp_obj.add_constraint(cons)
   return csp_obj, var



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
   var = []
   csp_obj = CSP("funpuzz")
   for i in range(funpuzz_grid[0][0]):
      row = []
      for j in range(funpuzz_grid[0][0]):
         domain = [1,2,3,4,5,6,7,8,9]
         to_add = Variable("variable_array[{}][{}]".format(i, j), domain)
         csp_obj.add_var(to_add)
         row.append(to_add)
      var.append(row)
   
   row_num = 0
   index_combinator = [x for x in range(0, funpuzz_grid[0][0])]
   index_combinations = list(itertools.combinations(index_combinator, 2))
   for var_row in var:
      for index_tup in index_combinations:
         cons = Constraint("AllDiff_row[{}]".format(row_num), [var_row[index_tup[0]], var_row[index_tup[1]]])
         sub_var = [var_row[index_tup[0]], var_row[index_tup[1]]]
         domains = []
         for variable in sub_var:
            domains.append(variable.domain())
         tuples = []
         for t in itertools.product(*domains):
            if len(t) == len(set(t)):
               tuples.append(t)
         cons.add_satisfying_tuples(tuples)
         csp_obj.add_constraint(cons)
      row_num += 1

   for i in range(len(var)):
      temp = []
      for j in range(len(var[i])):
         temp.append(var[j][i])
      for index_tup in index_combinations:
         cons = Constraint("AllDiff_column[{}]".format(i), [var_row[index_tup[0]], var_row[index_tup[1]]])
         sub_var = [var_row[index_tup[0]], var_row[index_tup[1]]]
         domains = []
         for variable in sub_var:
            domains.append(variable.domain())
         tuples = []
         for t in itertools.product(*domains):
            if len(t) == len(set(t)):
               tuples.append(t)
         cons.add_satisfying_tuples(tuples)
         csp_obj.add_constraint(cons)
   # var = []
   # csp_obj = CSP("funpuzz")
   # for i in range(funpuzz_grid[0][0]):
   #    row = []
   #    for j in range(funpuzz_grid[0][0]):
   #       domain = [1,2,3,4,5,6,7,8,9]
   #       to_add = Variable("variable_array[{}][{}]".format(i, j), domain)
   #       csp_obj.add_var(to_add)
   #       row.append(to_add)
   #    var.append(row)
   
   # row_num = 0
   # for var_row in var:
   #    cons = Constraint("AllDiff_row[{}]".format(row_num), var_row)
   #    domains = []
   #    for variable in var_row:
   #       domains.append(variable.domain())
   #    tuples = []
   #    for t in itertools.product(*domains):
   #       if len(t) == len(set(t)):
   #          tuples.append(t)
   #    cons.add_satisfying_tuples(tuples)
   #    csp_obj.add_constraint(cons)
   #    row_num += 1

   # for i in range(len(var)):
   #    temp = []
   #    for j in range(len(var[i])):
   #       temp.append(var[j][i])
   #    cons = Constraint("AllDiff_column[{}]".format(i), temp)
   #    domains = []
   #    for variable in temp:
   #       domains.append(variable.domain())
   #    tuples = []
   #    for t in itertools.product(*domains):
   #       if len(t) == len(set(t)):
   #          tuples.append(t)
   #    cons.add_satisfying_tuples(tuples)
   #    csp_obj.add_constraint(cons)
   
   cage_num = 0
   for i in range(1, len(funpuzz_grid)):
      cage = funpuzz_grid[i]
      var_list = []
      domain_list = []
      for element_index in range(len(cage) - 2):
         element = cage[element_index]
         row_num = element//10 - 1
         col_num = element%10 - 1
         var_list.append(var[row_num][col_num])
         domain_list.append(var[row_num][col_num].domain())
      con = Constraint("CageCon[{}]".format(cage_num), var_list)
      operator = cage[len(cage)-1]
      target = cage[len(cage)-2]
      tuples = []
      for t in itertools.product(*domain_list):
         if operator == 0:
            total = 0
            for element in t:
               total += element
            if total == target:
               tuples.append(t)
         elif operator == 1:
            total = t[0]
            for index in range(1, len(t)):
               total -= t[index]
            if total == target:
               tuples.append(t)
         elif operator == 2:
            total = t[0]
            for index in range(1, len(t)):
               total /= t[index]
            if total == target:
               tuples.append(t)
         elif operator == 3:
            total = 1
            for element in t:
               total *= element
            if total == target:
               tuples.append(t)
      con.add_satisfying_tuples(tuples)
      csp_obj.add_constraint(con)
      cage_num += 1
   return csp_obj, var


