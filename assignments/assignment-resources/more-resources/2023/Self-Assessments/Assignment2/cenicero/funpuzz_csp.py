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
    funPuzz = CSP('funpuzz')
    size = (funpuzz_grid.pop(0))[0]
    # dom = {1,2,3,...,size}
    dom = range(1,size+1)
    t = []
    gridvars = []
    # First we add all of the variables
    for x in dom:
      row = []
      for y in dom:
         varname = str(x)+","+str(y)
         var = Variable(varname,dom)
         row.append(var)
         funPuzz.add_var(var)
         t.append((x,y))
      gridvars.append(row)
    # now we add all of the constraints
    sattuples = filter((lambda t: t[0] != t[1]),t) #all tuples where the two numbers are not equal
    #handle all of the vertical constraints first
    for x in range(size):
      for y in range(size-1):
         v1 = gridvars[x][y]
         v2 = gridvars[x][y+1]
         cn = str(v1) + " to " + str(v2)
         c = Constraint(cn,[v1,v2])
         c.add_satisfying_tuples(sattuples)
         funPuzz.add_constraint(c)
    #handle all of the horizontal constraints
    for x in range(size-1):
      for y in range(size):
         v1 = gridvars[x][y]
         v2 = gridvars[x+1][y]
         cn = str(v1) + " to " + str(v2)
         c = Constraint(cn,[v1,v2])
         c.add_satisfying_tuples(sattuples)
         funPuzz.add_constraint(c)
    funpuzz_grid.insert(0,[size])
    return funPuzz, gridvars


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
    funPuzz = CSP('funpuzz')
    size = (funpuzz_grid.pop(0))[0]
    # dom = {1,2,3,...,size}
    dom = range(1,size+1)
    gridvars = [] #2d array of variables
    # First we add all of the variables
    for x in dom:
      row = []
      for y in dom:
         varname = str(x)+","+str(y)
         var = Variable(varname,dom)
         row.append(var)
         funPuzz.add_var(var)
      gridvars.append(row)
    # we have to generate a list of size-tuples.
    # We have a helper function which generates all possible
    # permutations of the list [1,2,3,...,size], which will be
    # very useful for the all-different constraints
    sattuples = permutes(range(1,size+1))
    # Now we generate the n-ary all-different constraints, first the rows
    for x in range(size):
      cname = "Row " + str(x+1)
      c = Constraint(cname,gridvars[x])
      c.add_satisfying_tuples(sattuples)
      funPuzz.add_constraint(c)
    for y in range(size):
      cname = "Col " + str(y+1)
      col = []
      for x in range(size):
         col.append(gridvars[x][y])
      c = Constraint(cname,col)
      c.add_satisfying_tuples(sattuples)
      funPuzz.add_constraint(c)
    funpuzz_grid.insert(0,[size])
    return funPuzz, gridvars

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
    funPuzz, gridvars = nary_ad_grid(funpuzz_grid)
    size = (funpuzz_grid.pop(0))[0]
    dom = range(1,size+1)

    for index in range(len(funpuzz_grid)):
      grid = funpuzz_grid[index]
      if len(grid) == 2:
         # first is the cell and the 2nd is the target
         cell = grid[0]
         target = [grid[1]]
         x = cell//10 #first digit
         y = cell%10        #2nd digit
         c = Constraint("Grid " + str(index),[gridvars[x-1][y-1]])
         c.add_satisfying_tuples([target])
         funPuzz.add_constraint(c)
      elif len(grid) > 2:
         mathop = grid.pop()
         target = grid.pop()
         sattuples = []
         if mathop == 0:
            sattuples = add_solver(target,dom,len(grid))
         elif mathop == 1:
            partial_tuples = subtraction_solver(target,dom,len(grid))
            for sltn in partial_tuples:
               permuted = permutes(sltn)
               for p in permuted:
                  if p in sattuples:
                     continue
                  sattuples.append(p)
         elif mathop == 2:
            partial_tuples = div_solver(target,dom,len(grid))
            for sltn in partial_tuples:
               permuted = permutes(sltn)
               for p in permuted:
                  if p in sattuples:
                     continue
                  sattuples.append(p)
         elif mathop == 3:
            sattuples = multiply_solver(target,dom,len(grid))
         scope = [] # add all of the vars in the grid to the scope
         for cell in grid:
            x = cell//10 #first digit
            y = cell%10        #2nd digit
            scope.append(gridvars[x-1][y-1])
         c = Constraint("Grid " + str(index),scope)
         c.add_satisfying_tuples(sattuples)
         funPuzz.add_constraint(c)
         # add back target and op
         grid.append(target)
         grid.append(mathop)
    funpuzz_grid.insert(0,[size])
    return funPuzz, gridvars

# Helpers below!!

def permutes(dom):
   # Generates a list of all permutations of a set dom
   if len(dom) == 1:
      return [dom]
   all_sltns = []
   for x in dom:
      new_dom = list(filter((lambda i: i != x),dom)) #dom without x
      curr_sltns = permutes(new_dom)
      for s in curr_sltns:
         all_sltns.append(s + [x])
   return all_sltns

def add_solver(curr_target,dom,n):
   #generate a list of all tuples of n numbers in dom where they add up to curr_target
   if n == 1:
      # return [[i]] where i == curr_target, if it is not in dom, then it returns []
      if curr_target in dom:
         return [[curr_target]]
      else:
         return None
   sltns = []
   for x in dom:
      new_target = curr_target - x
      partial_sltns = add_solver(new_target,dom,n-1)
      if partial_sltns is None:
         continue
      for s in partial_sltns:
         sltns.append(s + [x])
   return sltns

def subtraction_solver(curr_target,dom,n):
   #generate a list of all tuples of n numbers in dom where applying substraction
   #from the left will result in curr_target
   if n == 1:
      # return [[i]] where i == curr_target, if it is not in dom, then it returns []
      if curr_target in dom:
         return [[curr_target]]
      else:
         return None
   sltns = []
   for x in dom:
      # we want that substraction_solver(rest) - x = curr_target,
      # so new target is curr_target + x
      new_target = curr_target + x
      partial_sltns = subtraction_solver(new_target,dom,n-1)
      if partial_sltns is None:
         continue
      for s in partial_sltns:
         sltns.append(s + [x])
   return sltns

def multiply_solver(curr_target,dom,n):
   #generate a list of all tuples of n numbers in dom where they multiply to curr_target
   if n == 1:
      # return [[i]] where i == curr_target, if it is not in dom, then it returns []
      if curr_target in dom:
         return [[curr_target]]
      else:
         return None
   sltns = []
   for x in dom:
      # disregard any values of x that is not a factor of curr_target
      if curr_target % x != 0:
         continue
      # we can safely divide curr_target by x to get an integer
      # we sure hope 0 isnt in dom though!
      new_target = curr_target//x
      partial_sltns = multiply_solver(new_target,dom,n-1)
      if partial_sltns is None:
         continue
      for s in partial_sltns:
         sltns.append(s + [x])
   return sltns

def div_solver(curr_target,dom,n):
   #generate a list of all tuples of n numbers in dom where dividing the numbers
   #from the left will result in curr_target
   if n == 1:
      # return [[i]] where i == curr_target, if it is not in dom, then it returns []
      if curr_target in dom:
         return [[curr_target]]
      else:
         return None
   sltns = []
   for x in dom:
      # disregard any values of x that is not a factor of curr_target
      new_target = curr_target*x
      partial_sltns = div_solver(new_target,dom,n-1)
      if partial_sltns is None:
         continue
      for s in partial_sltns:
         sltns.append(s + [x])
   return sltns