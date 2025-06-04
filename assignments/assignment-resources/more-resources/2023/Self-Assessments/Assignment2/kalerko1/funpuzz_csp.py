#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from itertools import combinations, permutations
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
   board_length = funpuzz_grid[0][0]
   variable_array = []
   # print(board_length)
   valid_tuples = get_valid_tuples(board_length)
   # print(valid_tuples)
   flat_list = []

   for row in range(board_length):
      row_list = []
      for col in range (board_length):
         current_var = Variable(str(row)+str(col), list(range(1, board_length + 1)))
         row_list.append(current_var)
         flat_list.append(current_var)
      variable_array.append(row_list)
   
   csp = CSP("binary",flat_list)
   current_var = variable_array[0][0]

   for row in range(board_length):
      for col in range (board_length):
         current_var = variable_array[row][col]
         for k in range(col + 1, board_length):
            next_var = variable_array[row][k]
            x = Constraint("consCol",[current_var,next_var])
            #print("consCol",current_var,next_var)
            x.add_satisfying_tuples(valid_tuples)
            csp.add_constraint(x)

         for m in range(row + 1, board_length):
            next_var = variable_array[m][col]
            x = Constraint("consRow",[current_var,next_var])
            #print("consRow",current_var,next_var)
            x.add_satisfying_tuples(valid_tuples)
            csp.add_constraint(x)
   
   return csp, variable_array

         # if prev_var != None:
         #    x = Constraint("cons",[prev_var, current_var])
         #prev_var = current_var

   # for cage_cons_list in funpuzz_grid[1:]:
   #    for cage_cons in cage_cons_list:
   #       cellA = cage_cons[0]
   #       cellB = cage_cons[1]    
   #       A_row = cellA / 10
   #       A_col = cellA % 10
   #       varA = variable_array[A_row][A_col]
   #       B_row = cellB / 10
   #       B_col = cellB % 10
   #       varB = variable_array[B_row][B_col]
   #       total = cage_cons[2]
   #       x = Constraint("cons1",[varA, varB])

def get_valid_tuples(n, type=0):
   tuples = []

   if type == 0:
      for i in range(1, n+1):
         for j in range(1, n+1):
            if i != j:
               tuples.append((i, j))
               tuples.append((j, i))
   elif type == 1:
      #make list up to n
      lists = list(range(1,n+1))
      tuples =  list(permutations(lists))

   return tuples

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
   board_length = funpuzz_grid[0][0]
   variable_array = []
   #print(board_length)
   valid_tuples = get_valid_tuples(board_length, 1)
   #print("tuples: ", valid_tuples)
   flat_list = []
   col_list = []

   for row in range(board_length):
      row_list = []
      for col in range (board_length):
         current_var = Variable(str(row)+str(col), list(range(1, board_length + 1)))
         row_list.append(current_var)
         flat_list.append(current_var)
      variable_array.append(row_list)
   
   csp = CSP("n-ary",flat_list)

   for row in range(board_length):
      x = Constraint("consRow",variable_array[row])
      x.add_satisfying_tuples(valid_tuples)
      #print(variable_array[row])

      for col in range(board_length):
         col_list.append(variable_array[col][row])
      
      y = Constraint("consCol",col_list)
      y.add_satisfying_tuples(valid_tuples)
      #print(col_list)

      csp.add_constraint(x)
      csp.add_constraint(y)
      col_list = []
      
   return csp, variable_array

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
   board_length = funpuzz_grid[0][0]
   csp, variable_array = nary_ad_grid(funpuzz_grid)

   for cage_cons_list in funpuzz_grid[1:]:
         cage_cons_len = len(cage_cons_list)
         var_list = []

         for cellA in cage_cons_list[:-2]:
            A_row = cellA // 10 - 1
            A_col = cellA % 10 - 1
            varA = variable_array[A_row][A_col]
            var_list.append(varA)

         x = Constraint("cons1", var_list)
         valid_tuples = get_valid_tuples_funpuzz(board_length, cage_cons_len, cage_cons_list)
         print("funpuzz: ", valid_tuples)
         x.add_satisfying_tuples(valid_tuples)
         csp.add_constraint(x)
   
   return csp, variable_array

def operate(operation,seq,total):
      answer = False
      
      if operation == 0: 
         answer = sum(seq)

      if operation == 1: 
         answer = seq[0]
         for i in seq[1:]:
            answer -= i
            answer = abs(answer) 


      if operation == 2: 
         answer = seq[0]
         for i in seq[1:]:
            answer /= i 
         return True


      if operation == 3:
         answer = seq[0]
         for i in seq[1:]:
            answer *= i  

      
      if answer == total:
         return True
      return False

def get_valid_tuples_funpuzz(n, cage_len, cage_cons):
   if cage_cons[-1] > 2:
      print(cage_cons)
   operation = cage_cons.pop()
   total = cage_cons.pop()
   lists = list(range(1,n+1))
   tuples = []
   
   #make list of all possible permutations of list with len cage_len minus the two pops
   for seq in permutations(lists, cage_len - 2):
      #check if satisfies the constraint
      if operate(operation, seq, total):
         tuples.append(seq)
   return tuples
