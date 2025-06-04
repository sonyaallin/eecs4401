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
    variable_array = []
    variables = []
    
    dimension = funpuzz_grid[0][0]
    
    domain = []
    i = 1
    while i < dimension+1:
       domain.append(i)
       i += 1

    constraints = []
    column = []
    for i in range(0, dimension):
       column.append([])

    i = 1
    while i < (dimension + 1):
       j = 1
       new = []
       while j <= dimension:
          var = Variable(str(i) + str(j), domain)
          column[j-1].append(var)
          new.append(var)
          variables.append(var)
          j += 1
       row_cons = ne_constraint("Row" + str(i), new)
       constraints.extend(row_cons)
       variable_array.append(new)
       i += 1

    for i in range(0, dimension):
       constraints.extend(ne_constraint("Column" + str(i), column[i]))
   
    cps_funpuzz = CSP("funpuzz_grid", variables)
    for i in constraints:
       cps_funpuzz.add_constraint(i)

    return cps_funpuzz, variable_array

def ne_constraint(type, variables):

   cons = []
   count = 0
   while count < len(variables)-1:
      for variable in variables:
         if variables[count] != variable:
            con = Constraint(type + str(count), [variables[count], variable])
            ad_constraint(con)
      count += 1
   return cons


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
    variable_array = []
    variables = []
    
    dimension = funpuzz_grid[0][0]
    
    domain = []
    i = 1
    while i < dimension+1:
       domain.append(i)
       i += 1

    constraints = []
    column = []
    for i in range(0, dimension):
       column.append([])

    i = 1
    while i < (dimension + 1):
       j = 1
       new = []
       while j <= dimension:
          var = Variable(str(i) + str(j), domain)
          column[j-1].append(var)
          new.append(var)
          variables.append(var)
          j += 1
       row = Constraint("Row" + str(i), new)
       constraints.append(row)
       variable_array.append(new)
       i += 1

    for i in range(0, dimension):
       constraints.append(Constraint("Column" + str(i), column[i]))
   
    cps_funpuzz = CSP("funpuzz_grid", variables)
    for i in constraints:
       ad_constraint(i)
       cps_funpuzz.add_constraint(i)

    return cps_funpuzz, variable_array

def ad_constraint(constraint):
   vars = constraint.get_scope()
   selected = []
   for var in vars:
      selected.append(var.domain())
   possibilities = itertools.product(*selected)
   satisfying = []
   for option in possibilities:
      flag = True
      for n in option:
         if option.count(n) > 1:
            flag = False
            break
      if flag:
         satisfying.append(option)
   constraint.add_satisfying_tuples(satisfying)


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
    cps_funpuzz, variable_array = nary_ad_grid(funpuzz_grid)
    print(variable_array)
    count = 0

    for cage in funpuzz_grid[1:]:
       if len(cage) == 2:
          i = str(cage[0])[0] - 1
          j = str(cage[0])[1] - 1
          cage_con = Constraint("Cage" + str(count), [variable_array[i][j]])
          cps_funpuzz.add_constraint(cage_con)
          variable_array[i][j].assign(cage[1])
       else:
          operation = cage[-1]
          target = cage[-2]

          con_vars = []
          con_dom = []

          for val in cage[:-2]:
             i = int(str(val)[0]) - 1
             j = int(str(val)[1]) - 1
             con_vars.append(variable_array[i][j])
             con_dom.append(variable_array[i][j].domain())

          cage_con = Constraint("Cage" + str(count), con_vars)
          cage_tups = []

          possibilities = itertools.product(*con_dom)
          
          for option in possibilities:
             if operation == 0:      # sum
                total = 0
                for opt in option:
                   total = total + opt
                if total == target:
                   cage_tups.append(option)
             elif operation == 1:      # difference -- permutation matters.
                for choices in itertools.permutations(option):
                   difference = choices[0]
                   for choice in choices[1:]:
                      difference -= choice
                   if difference == target:
                      cage_tups.append(option)
             elif operation == 2:      # quotient -- permutation matters.
                for choices in itertools.permutations(option):
                   quotient = choices[0]
                   for choice in choices[1:]:
                      quotient = quotient / choice
                   if quotient == target:
                      cage_tups.append(option)
             elif operation == 3:         # product
                mul = 1
                for opt in option:
                   mul = mul * opt
                if mul == target:
                   cage_tups.append(option)
          cage_con.add_satisfying_tuples(cage_tups)
          cps_funpuzz.add_constraint(cage_con)
       count += 1

    return cps_funpuzz, variable_array


