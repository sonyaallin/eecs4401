#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''

from cspbase import *
from itertools import permutations
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
   n = funpuzz_grid[0][0]
   Vars= []
   constraints=[]
   domain = [x for x in range(1, n+1)]
   satisify = [sat for sat in permutations(domain, 2)]
   # print(list(satisify))
   variable_array=[]
   for i in range(1, n+1):
      row=[]
      for k in range(1, n+1):
         Vars.append(Variable(str(i)+str(k), domain))
         row.append(Vars[-1])
      variable_array.append(row)
   for col in range(n):
      for row1 in range(n):
         for row2 in range(row1+1,n):
            var1= variable_array[col][row1]
            var2=variable_array[col][row2]
            # print( var1.name, var2.name)
            c= Constraint(""+ var1.name+ " and "+ var2.name, [var1,var2])
            c.add_satisfying_tuples(list(satisify))
            constraints.append(c)
   # print("--------")
   for row in range(n):
      for col1 in range(n):
         for col2 in range(col1+1,n):
            var1= variable_array[col1][row]
            var2= variable_array[col2][row]
            # print( var1.name, var2.name)
            c= Constraint(""+ var1.name+ " and "+ var2.name, [var1,var2])
            c.add_satisfying_tuples(list(satisify))
            constraints.append(c)
   csp = CSP("Binary NE Fuzzpuzz No cages", Vars)
   for c in constraints:
      # print(c.name, c.sat_tuples)
      csp.add_constraint(c)
   return csp, variable_array


   pass


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
   n = funpuzz_grid[0][0]
   Vars= []
   constraints=[]
   domain = [x for x in range(1, n+1)]
   satisify = [sat for sat in permutations(domain, n)]
   variable_array=[]
   for i in range(1, n+1):
      row= []
      for k in range(1, n+1):
         Vars.append(Variable(str(i)+str(k), domain))
         row.append(Vars[-1])
      variable_array.append(row)
      c= Constraint("Row "+str(i), Vars[-n:])
      c.add_satisfying_tuples(list(satisify))
      constraints.append(c)
   for i in range(n):
      vs= Vars[i::n]
      c= Constraint("Collumn "+str(i), vs)
      c.add_satisfying_tuples(list(satisify))
      constraints.append(c)
   csp = CSP("Narray Fuzzpuzz", Vars)
   for c in constraints:
      csp.add_constraint(c)
   return csp, variable_array


def difference(t):
   diffs=[]
   for i in range(len(t)):
      diff= t[i]
      for k in range(len(t)):
         if k!= i:
            diff-=t[k]
      diffs.append(int(diff))
   # print(quots)
   return diffs
def product(t):
   prod = 1
   for i in t:
      prod*=i
   return prod
def quotient(t):
   # print(t)
   quots=[]
   for i in range(len(t)):
      quot= t[i]
      for k in range(len(t)):
         if k!= i:
            quot= quot/t[k]
      quots.append(int(quot))
   # print(quots)
   return quots
   quot= t[0]
   for i in range(1, len(t)):
      quot= quot/t[i]
   return quot 

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
   n = funpuzz_grid[0][0]
   Vars= []
   constraints=[]
   domain = [x for x in range(1, n+1)]
   satisify = [sat for sat in permutations(domain, 2)]
   # print(list(satisify))
   variable_array=[]
   for i in range(1, n+1):
      row=[]
      for k in range(1, n+1):
         Vars.append(Variable(str(i)+str(k), domain))
         row.append(Vars[-1])
      variable_array.append(row)
   for col in range(n):
      for row1 in range(n):
         for row2 in range(row1+1,n):
            var1= variable_array[col][row1]
            var2=variable_array[col][row2]
            # print( var1.name, var2.name)
            c= Constraint(""+ var1.name+ " and "+ var2.name, [var1,var2])
            c.add_satisfying_tuples(list(satisify))
            constraints.append(c)
   # print("--------")
   for row in range(n):
      for col1 in range(n):
         for col2 in range(col1+1,n):
            var1= variable_array[col1][row]
            var2= variable_array[col2][row]
            # print( var1.name, var2.name)
            c= Constraint(""+ var1.name+ " and "+ var2.name, [var1,var2])
            c.add_satisfying_tuples(list(satisify))
            constraints.append(c)
   csp = CSP("Binary NE Fuzzpuzz With Cages", Vars)
   for c in constraints:
      # print(c.name, c.sat_tuples)
      csp.add_constraint(c)

   
   for i in range(1, len(funpuzz_grid)):
      cage = funpuzz_grid[i]
      vs=[]
      
      for v in cage[:-2]:
         # print(v, n, 10, v%10,(v-v%10))
         # print(((v-v%10)//10-1), v%10-1, v)
         vs.append(Vars[((v-v%10)//10-1)*n+v%10-1])
      # print("cage", cage, len(vs))
      if cage[-1]== 0:
         result = [seq  for seq in permutations(domain*n, len(vs))
            if sum(seq) == cage[-2]]
      elif cage[-1]==1:
         result = [seq  for seq in permutations(domain*n, len(vs))
            if cage[-2] in difference(seq)]
      elif cage[-1]==2:
         result = [seq  for seq in permutations(domain*n, len(vs))
            if cage[-2] in quotient(seq)]
      elif cage[-1]==3:
         result = [seq  for seq in permutations(domain*n, len(vs))
            if product(seq) == cage[-2]]
      # print(result)
      c= Constraint("Cage "+str(i-1), vs)
      c.add_satisfying_tuples(result)
      # print(c.sat_tuples)
      constraints.append(c)
      csp.add_constraint(c)
   #    print(c)
   # print(Vars)
   # csp.print_all()
   return csp, variable_array


