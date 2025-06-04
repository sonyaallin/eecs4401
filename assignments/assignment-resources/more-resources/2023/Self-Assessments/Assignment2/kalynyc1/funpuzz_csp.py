#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from itertools import *
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
   dimension = funpuzz_grid[0][0]

   funpuzz_csp = None
   variable_array = []
   values_array = []
   constraints_array = []
   tuple_array = []

   for y in range(dimension):
      temp = []
      for x in range(dimension):
         new_var = Variable(str(y) + str(x), domain = list(range(1, dimension + 1)))
         temp.append(new_var)
         values_array.append(new_var)
      variable_array.append(temp)

   funpuzz_csp = CSP("binary_ne_grid", values_array)

   for tuple in permutations(list(range(1, dimension + 1)), 2):
      tuple_array.append(tuple)

   for y in range(dimension):
      for x in range(dimension):
         for z in range(x + 1, dimension):
            row_constraint = Constraint("row-" + str(y) + str(x) + str(z), [variable_array[y][x], variable_array[y][z]])
            row_constraint.add_satisfying_tuples(tuple_array)
            constraints_array.append(row_constraint)

            col_constraint = Constraint("col-" + str(y) + str(x) + str(z), [variable_array[x][y], variable_array[z][y]])
            col_constraint.add_satisfying_tuples(tuple_array)
            constraints_array.append(col_constraint)

   for constraint in constraints_array:
      funpuzz_csp.add_constraint(constraint)

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
    dimension = funpuzz_grid[0][0]

    funpuzz_csp = CSP("nary_ad_grid")
    variable_array = []
    tuple_array = []
    
    variables_x = [[] for i in range(dimension)]
    variables_y= [[] for i in range(dimension)]

    for y in range(1, dimension + 1):
        temp = []
        for x in range(1, dimension + 1):
            new_var = Variable(str(y) + str(x), domain = list(range(1, dimension + 1)))

            variables_x[y - 1].append(new_var)
            variables_y[x - 1].append(new_var)

            funpuzz_csp.add_var(new_var)
            temp.append(new_var)

        variable_array.append(temp)

    for tuple in permutations(list(range(1, dimension + 1)), dimension):
        tuple_array.append(tuple)

    for i in range(1, dimension + 1):
        row_constraint = Constraint(str(i), variables_x[i - 1])
        row_constraint.add_satisfying_tuples(tuple_array)
        funpuzz_csp.add_constraint(row_constraint)

        col_constraint = Constraint(str(i), variables_y[i - 1])
        col_constraint.add_satisfying_tuples(tuple_array)
        funpuzz_csp.add_constraint(col_constraint)

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

   Note that this model does require implementation of cage constraints.
   """
   dimension = funpuzz_grid[0][0]

   funpuzz_csp = CSP("funpuzz_csp_model")
   variable_array = []
   constraints_array = []
   num_cages = len(funpuzz_grid)
    
   for y in range(1, dimension + 1):
      temp = []
      for x in range(1, dimension + 1):
         temp.append(Variable(str(y) + str(x), domain = list(range(1, dimension + 1))))
      variable_array.append(temp)

   for cage in range(1, num_cages):
      if(len(funpuzz_grid[cage]) == 2):
         x = int(str(funpuzz_grid[cage][0])[0]) - 1
         y = int(str(funpuzz_grid[cage][0])[1]) - 1
         result = funpuzz_grid[cage][1]
         variable_array[y][x] = Variable(str(y) + str(x), [result])
      else:
         math_op = funpuzz_grid[cage][-1]
         result = funpuzz_grid[cage][-2]
         variables = []
         var_domain = []

         for cell in range(len(funpuzz_grid[cage]) - 2):
               x = int(str(funpuzz_grid[cage][cell])[0]) - 1
               y = int(str(funpuzz_grid[cage][cell])[1]) - 1
               variables.append(variable_array[x][y])
               var_domain.append(variable_array[x][y].domain())

         cross_product = product(*var_domain)
         constr = Constraint("cage-" + str(cage), variables)
         cage_vars = []

         for domain in cross_product:
               if (math_op == 0):   # addition
                  ans = 0
                  for num in domain:
                     ans += num
                  if (ans == result):
                     cage_vars.append(domain)
               elif (math_op == 1): # subtraction
                  for num in permutations(domain):
                     ans = num[0]
                     for n in range(1, len(num)):
                           ans -= num[n]
                     if(ans == result):
                           cage_vars.append(domain)
               elif (math_op == 2): # division
                  for num in permutations(domain):
                     ans = num[0]
                     for n in range(1, len(num)):
                           ans = ans/num[n]
                     if(ans == result):
                           cage_vars.append(domain)
               elif (math_op == 3): # multiplication
                  ans = 1
                  for num in domain:
                     ans *= num
                  if (ans == result):
                     cage_vars.append(domain)

         constr.add_satisfying_tuples(cage_vars)
         constraints_array.append(constr)

   for y in range(dimension):
      for x in range(dimension):
         for z in range(len(variable_array[y])):
               if (z > x):
                  r_v1 = variable_array[y][x]
                  r_v2 = variable_array[y][z]
                  row_constraint = Constraint("row-" + str(y + 1) + str(x + 1) + str(y + 1) + str(z + 1), [r_v1, r_v2])
                  tuples = []

                  for domain in product(r_v1.domain(), r_v2.domain()):
                     if domain[0] != domain[1]:
                           tuples.append(domain)

                  row_constraint.add_satisfying_tuples(tuples)
                  constraints_array.append(row_constraint)
               if (z > y):
                  c_v1 = variable_array[y][x]
                  c_v2 = variable_array[z][x]
                  col_constraint = Constraint("col-" + str(y + 1) + str(x + 1) + str(z + 1) + str(x + 1), [c_v1, c_v2])
                  tuples = []

                  for domain in product(c_v1.domain(), c_v2.domain()):
                     if domain[0] != domain[1]:
                           tuples.append(domain)

                  col_constraint.add_satisfying_tuples(tuples)
                  constraints_array.append(col_constraint)

   for row in variable_array:
      for var in row:
         funpuzz_csp.add_var(var)

   for cons in constraints_array:
      funpuzz_csp.add_constraint(cons)

   return funpuzz_csp, variable_array


