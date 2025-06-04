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
    
    grid_size = funpuzz_grid[0][0]
    variables = []
    variable_array = []
    domain = []
    constaints = []
    rows = {}
    columns = {}

    for i in range (1, grid_size + 1):
       variable_array.append([])

    for i in range(1, grid_size + 1):
       domain.append(i)

    tuples = []
    for index, num in enumerate(domain):
      for num1 in domain[index + 1:]:
                     tuples.append((num, num1))
                     tuples.append((num1, num))

    row = 1
    column = 1
    for j in range(1, grid_size * grid_size + 1):
       new_var_name = str(row) + str(column)
       new_var = Variable(new_var_name, domain)
       variables.append(new_var)
       variable_array[row - 1].append(new_var)
       if (not str(row) in rows):
         rows[str(row)] = [new_var]
       else:
         rows[str(row)].append(new_var)
       if (not str(column) in columns):
         columns[str(column)] = [new_var]
       else:
         columns[str(column)].append(new_var)
       if (column % grid_size == 0):
         column = 1
         row = row + 1
       else:
          column = column + 1

    num = 1
    for row in rows:
       num = num +1
       for i, var in enumerate(rows[row]):
            for var1 in rows[row][i + 1:]:
               new_con = Constraint('c' + str(num), [var, var1])
               new_con.add_satisfying_tuples(tuples)
               constaints.append(new_con)

    num = 1
    for column in columns:
         num = num+1
         for i, var in enumerate(columns[column]):
            for var1 in columns[column][i + 1:]:
               new_con = Constraint('c' + str(num), [var, var1])
               new_con.add_satisfying_tuples(tuples)
               constaints.append(new_con)

    funpuzz_csp = CSP("binary", variables)
    for c in constaints:
       funpuzz_csp.add_constraint(c)

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
    pass
    grid_size = funpuzz_grid[0][0]
    domain = []
    tuples = list(itertools.permutations(range(1, grid_size+1), grid_size))

    for i in range(1, grid_size + 1):
       domain.append(i)

    variables = []
    variable_array = []
    constaints = []
    rows = {}
    columns = {}

    for i in range (1, grid_size + 1):
       variable_array.append([])

    row = 1
    column = 1
    for j in range(1, grid_size * grid_size + 1):
       new_var_name = str(row) + str(column)
       new_var = Variable(new_var_name, domain)
       variables.append(new_var)
       variable_array[row - 1].append(new_var)
       if (not str(row) in rows):
         rows[str(row)] = [new_var]
       else:
         rows[str(row)].append(new_var)
       if (not str(column) in columns):
         columns[str(column)] = [new_var]
       else:
         columns[str(column)].append(new_var)
       if (column % grid_size == 0):
         column = 1
         row = row + 1
       else:
          column = column + 1

    num = 1
    for row in rows:
       num = num +1
       new_con = Constraint('c97' + str(num), rows[row])
       new_con.add_satisfying_tuples(tuples)
       constaints.append(new_con)

    num = 1
    for column in columns:
         num = num+1
         new_con = Constraint('c199' + str(num), columns[column])
         new_con.add_satisfying_tuples(tuples)
         constaints.append(new_con)

    funpuzz_csp = CSP("nary", variables)
    for c in constaints:
       funpuzz_csp.add_constraint(c)

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

    
    funpuzz_csp, var_array = binary_ne_grid(funpuzz_grid)
    grid_size = funpuzz_grid[0][0]
    funpuzz_csp.name = "funpuzz"

   
    for i in range(1, len(funpuzz_grid)):
      tuples = []
      constraint = funpuzz_grid[i]
      variables_con = constraint[0:-2]
      new_constraint_variables = []

      if (len(variables_con) == 0):
         row = int(str(constraint[0])[0])
         column = int(str(constraint[0])[1])
         new_constraint_variables.append(var_array[row-1][column-1])

         new_con = Constraint("c1" + str(constraint[0]) + str(i), new_constraint_variables)
         new_con.add_satisfying_tuples([(constraint[1],)])
         funpuzz_csp.add_constraint(new_con)
         continue

      for vc in variables_con:
         row = int(str(vc)[0])
         column = int(str(vc)[1])

         new_constraint_variables.append(var_array[row-1][column-1])


      value = constraint[-2]
      operator = constraint[-1]
      #permu = list(itertools.permutations(range(1, grid_size + 1), len(new_constraint_variables)))
      permu = list(itertools.product(range(1, grid_size + 1), repeat=len(new_constraint_variables)))
      equal = []
      sorted_equal = []
      
      if (operator == 0):
         for nums in permu[:]:
            if (sum(nums) == value):
               equal.append(nums)
      elif (operator == 1):
         for nums in permu[:]:
            final = nums[0]
            for i in nums[1:]:
               final = final - i
            if (final == value):
               equal.append(nums)
      elif (operator == 2):
         for nums in permu[:]:
            final = nums[0]
            for i in nums[1:]:
               final = final / i
            if (final == value):
               equal.append(nums)
      elif (operator == 3):
         for nums in permu[:]:
            final = nums[0]
            for i in nums[1:]:
               final = final * i
            if (final == value):
               equal.append(nums)

      for tuple in equal[:]:
         sorted_equal.append(sorted(tuple))

      same_row_or_column = []
      same_column = []
         

      for var in new_constraint_variables:
         for var1 in new_constraint_variables:
            if var != var1:
               if (var.name[0] == var1.name[0] or var.name[1] == var1.name[1]):
                  same_row_or_column.append((new_constraint_variables.index(var), new_constraint_variables.index(var1)))

      for per in permu[:]:
         if sorted(per) not in sorted_equal:
            permu.remove(per)
            
      for c in same_row_or_column[:]:
         for pe in permu[:]:
            if (pe[c[0]] == pe[c[1]]):
               permu.remove(pe)


     
      new_con = Constraint("c123" + str(constraint[0]) + str(i+1), new_constraint_variables)
      new_con.add_satisfying_tuples(permu)
      funpuzz_csp.add_constraint(new_con)
      # print(new_constraint_variables)
      # print("premu" + str(permu))
      # print(value)
   
    return funpuzz_csp, var_array


    


