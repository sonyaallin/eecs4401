#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from itertools import combinations, combinations_with_replacement, permutations
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
    variable_array = []
    csp = CSP("binary_csp")
    n = funpuzz_grid[0][0]
    for i in range(1, n + 1):
       temp = []
       for j in range(1, n + 1):
         var = Variable(str(i)+str(j), range(1, n + 1))
         csp.add_var(var)
         temp.append(var)
       variable_array.append(temp)
    #unary constraint for variable at row 1 column 1
    cons = Constraint("unary", [variable_array[0][0]])
    cons.add_satisfying_tuples(permutations(range(1, n + 1), 1))
    csp.add_constraint(cons)
    #row constraints
    for i in range(1, n + 1):
       combs = combinations(range(1, n + 1), 2)
       for tuple in combs:
          var1 = variable_array[i - 1][tuple[0] - 1]
          var2 = variable_array[i - 1][tuple[1] - 1]
          var1_index = csp.vars.index(var1)
          var2_index = csp.vars.index(var2)
          name = "cons" + str(var1_index + 1) + str(var2_index + 1)
          scope = [var1, var2]
          cons = Constraint(name, scope)
          cons.add_satisfying_tuples(permutations(range(1, n + 1), 2))
          csp.add_constraint(cons)
    #column constraints
    for i in range(1, n + 1):
       combs = combinations(range(1, n + 1), 2)
       for tuple in combs:
          var1 = variable_array[tuple[0] - 1][i - 1]
          var2 = variable_array[tuple[1] - 1][i - 1]
          var1_index = csp.vars.index(var1)
          var2_index = csp.vars.index(var2)
          name = "cons" + str(var1_index + 1) + str(var2_index + 1)
          scope = [var1, var2]
          cons = Constraint(name, scope)
          cons.add_satisfying_tuples(permutations(range(1, n + 1), 2))
          csp.add_constraint(cons)
    return csp, variable_array


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
    csp = CSP("nary_csp")
    n = funpuzz_grid[0][0]
    for i in range(1, n + 1):
       temp = []
       for j in range(1, n + 1):
         var = Variable(str(i)+str(j), range(1, n + 1))
         csp.add_var(var)
         temp.append(var)
       variable_array.append(temp)
    #unary constraint for variable at row 1 column 1
    cons = Constraint("unary", [variable_array[0][0]])
    cons.add_satisfying_tuples(permutations(range(1, n + 1), 1))
    csp.add_constraint(cons)
    #row constraints
    for i in range(1, n + 1):
       name = "cons_row_" + str(i)
       scope = []
       for item in range(1, n + 1):
          var = variable_array[i - 1][item - 1]
          scope.append(var)
       cons = Constraint(name, scope)
       cons.add_satisfying_tuples(permutations(range(1, n + 1), n))
       csp.add_constraint(cons)
    #column constraints
    for i in range(1, n + 1):
       name = "cons_column_" + str(i)
       scope = []
       for item in range(1, n + 1):
          var = variable_array[item - 1][i - 1]
          scope.append(var)
       cons = Constraint(name, scope)
       cons.add_satisfying_tuples(permutations(range(1, n + 1), n))
       csp.add_constraint(cons)
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
    csp, variable_array = binary_ne_grid(funpuzz_grid)
    n = funpuzz_grid[0][0]
    for i in range(1, len(funpuzz_grid)):
       if len(funpuzz_grid[i]) == 2:
          row = (funpuzz_grid[i][0]//10) - 1
          col = (funpuzz_grid[i][0]%10) - 1
          var = variable_array[row][col]
          cons = Constraint("unary_cons", [var])
          cons.add_satisfying_tuples([(funpuzz_grid[i][1],)])
          csp.add_constraint(cons)
       else:
          target = funpuzz_grid[i][-2]
          op = funpuzz_grid[i][-1]
          scope = []
          for j in range(len(funpuzz_grid[i]) - 2):
             row = (funpuzz_grid[i][j]//10) - 1
             col = (funpuzz_grid[i][j]%10) - 1
             var = variable_array[row][col]
             scope.append(var)
          cons = Constraint("cons_cage_" + str(i), scope)
          satisfying_tuples = check_tuples(scope, target, op, n)
          cons.add_satisfying_tuples(satisfying_tuples)
          csp.add_constraint(cons)
    return csp, variable_array


def check_tuples(scope, target, op, n):
    """
    Return a list of tuple values that satisfy the given cage constraint
    """
    result = []
    combs = combinations_with_replacement(range(1, n + 1), len(scope))
    for comb in combs:
       if op == 0 and sum(list(comb)) == target:
          result.append(comb)
          result.extend(permutations(comb, len(comb)))
       elif op == 1:
          for i in range(len(comb)):
            diff = comb[i]
            for j in range(len(comb)):
               if i != j:
                  diff -= comb[j]
            if diff == target:
               result.append(comb)
               result.extend(permutations(comb, len(comb)))
       elif op == 2:
          for i in range(len(comb)):
            quotient = comb[i]
            for j in range(len(comb)):
               if i != j:
                  quotient /= comb[j]
            if quotient == target:
               result.append(comb)
               result.extend(permutations(comb, len(comb)))
       elif op == 3:
          for i in range(len(comb)):
            product = comb[i]
            for j in range(len(comb)):
               if i != j:
                  product *= comb[j]
            if product == target:
               result.append(comb)
               result.extend(permutations(comb, len(comb)))
    return result

