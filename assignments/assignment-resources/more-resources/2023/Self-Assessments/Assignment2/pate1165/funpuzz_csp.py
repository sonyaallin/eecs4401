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
    funpuzz_csp = CSP("funpuzz")
    variable_array = []
    domain = [i for i in range(1,funpuzz_grid[0][0]+1)]

    for x in range(1,funpuzz_grid[0][0]+1):
       temp = []
       for y in range(1,funpuzz_grid[0][0]+1):
          var = Variable(str(x)+str(y),domain)
          funpuzz_csp.add_var(var)
          temp.append(var)
       variable_array.append(temp)

    
    #Go through row by row
    for row in range(1,funpuzz_grid[0][0] + 1):
      for x in range(1,funpuzz_grid[0][0] + 1):
         for y in range(1,funpuzz_grid[0][0] + 1):
            if x != y:
               cons_name = str(x)+str(row)+str(x)+str(y)
               con = Constraint(cons_name,[variable_array[row-1][x-1],variable_array[row-1][y-1]])
               con.add_satisfying_tuples(itertools.permutations(domain,2))

               funpuzz_csp.add_constraint(con)



    for col in range(1,funpuzz_grid[0][0] + 1):
      for x in range(1,funpuzz_grid[0][0] + 1):
         for y in range(1,funpuzz_grid[0][0] + 1):
            if x != y:
               cons_name = str(x)+str(col)+str(x)+str(y)
               con = Constraint(cons_name,[variable_array[x-1][col-1],variable_array[y-1][col-1]])
               con.add_satisfying_tuples(itertools.permutations(domain,2))
    
               funpuzz_csp.add_constraint(con)

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
    funpuzz_csp = CSP("funpuzz")
    col_var = []
    variable_array = []
    domain = [i for i in range(1,funpuzz_grid[0][0]+1)]

    #Get all combinations tuple
    for z in range(1,funpuzz_grid[0][0]+1):
       col_var.append([])


    #Go through each box
    for x in range(1,funpuzz_grid[0][0]+1):
      row_var = []
      temp = []
      for y in range(1,funpuzz_grid[0][0]+1):
         
         sx = str(x)
         sy = str(y)
         #Create Var for this box
         var = Variable(sx+sy,domain)

         #Add var to array, col, row vars and the csp
         temp.append(var)
         col_var[x-1].append(var)
         funpuzz_csp.add_var(var)
         row_var.append(var)
      variable_array.append(temp)
      #create constrains for the row   
      row_cons = Constraint(str(x),row_var)
      row_cons.add_satisfying_tuples(itertools.permutations(row_var))
      funpuzz_csp.add_constraint(row_cons)

    #Create and add col const
    for x in col_var:
       col_cons = Constraint(str(col_var.index(x))*2,x)
       col_cons.add_satisfying_tuples(itertools.permutations(x))
       funpuzz_csp.add_constraint(col_cons)

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

    funpuzz_csp,variable_array = binary_ne_grid(funpuzz_grid)
    funpuzz_grid.pop(0)

    i = 1
    domain = [i for i in range(1,funpuzz_grid[0][0]+1)]

    for cage in funpuzz_grid:
       nums = cage[:-2] 
       oper = cage[-1]
       total = cage[-2] 
       cage_var = []

       for n in nums:
          n = str(n)
          x = int(n[0])
          y = int(n[1])
          cage_var.append(variable_array[x-1][y-1])

       #Got all vars now create const
       cons = Constraint('cage'+str(i),cage_var)
       combos = itertools.product(domain,repeat=len(nums)) 
       i+=1
       final_perms = []
       for combo in combos:
          #Add
          if int(oper) == 0:
             if sum(combo) == total:
                final_perms.append(combo)
          elif int(oper) == 1:
               sub = combo[0]
               for x in range(1,len(combo)):
                  sub -= combo[x]
               if sub == total:
                  final_perms.append(combo)
                  final_perms.extend(list(itertools.permutations(combo)))
          elif int(oper) == 2:
             div = combo[0]
             for x in range(1,len(combo)):
                div = div/combo[x]
             if div == total:
                final_perms.append(combo)
                final_perms.append(combo)
                final_perms.extend(list(itertools.permutations(combo)))
          elif int(oper) == 3:
             mult = combo[0]
             for x in range(1,len(combo)):
                mult = mult*combo[x]
             if mult == total:
                final_perms.append(combo)
       cons.add_satisfying_tuples(final_perms)
       funpuzz_csp.add_constraint(cons)
   

    return funpuzz_csp, variable_array



             
       



    

