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
    n = funpuzz_grid[0][0]
    var = []
    d = list(range(1,n+1))
    for i in range(n):
        var.append([])
        for j in range(n):
            v = Variable(str(i*n+j), d)
            var[i].append(v)
    lst = []
    for i in var:
        lst = lst + i
    csp = CSP("funpuzz_csp", lst)
    sat = []
    for i in range(1,n+1):
        for j in range(1,n+1):
            if i!=j:
                sat.append((i,j))
    cons = []

    for i in range(n):
        for j in range(n-1):
            for k in range(1,n-j):
                scope = [var[i][j], var[i][j+k]]
                c = Constraint("r,r"+str(i)+"c"+str(j)+"n"+str(k), scope)
                cons.append(c)
                scope = [var[j][i],var[j+k][i]]
                c = Constraint("c,r"+str(i)+"c"+str(j)+"n"+str(k), scope)
                cons.append(c)
    for con in cons:
        con.add_satisfying_tuples(sat)
        csp.add_constraint(con)

    return csp, var
    

                



    
    


    


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
    var = []
    d = list(range(1,n+1))
    for i in range(n):
        var.append([])
        for j in range(n):
            v = Variable(str(i*n+j), d)
            var[i].append(v)
    lst = []
    for i in var:
        lst = lst + i
    csp = CSP("funpuzz_csp", lst)
    sat = list(itertools.permutations(d))
    cons = []
    for i in range(n):
        scope1 = []
        scope2 = []
        for j in range(n):
            scope1.append(var[i][j])
            scope2.append(var[j][i])
        c = Constraint("r"+str(i), scope1)
        cons.append(c)
        c = Constraint("c"+str(i), scope2)
        cons.append(c)
    for con in cons:
        con.add_satisfying_tuples(sat)
        csp.add_constraint(con)

    return csp, var
        


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
    csp, var = nary_ad_grid(funpuzz_grid)
    k =1
    for c in funpuzz_grid[1:]:
        scope = []
        for v in c[:-2]:
            i = v//10 -1
            j = v%10 -1
            scope.append(var[i][j])
        sat = cage_helper(len(c)-2, c[-1],c[-2], n)
        con = Constraint(str(k), scope)
        for s in sat:
            con.add_satisfying_tuples(list(itertools.permutations(s)))
        csp.add_constraint(con)
        k+=1
    return csp, var






def cage_helper(length, mode,total, n, lst = []):
    ''''helper to return list of lists that satsify the cage constraint'''

    sat = []
    m1 = 1
    m2 = n+1
    if lst != []:
        if mode == 0:
            s = sum(lst)
            if length ==0 and s == total:
                return lst
            elif length == 0:
                return []
            elif s >= total:
                return []
            m2 = max(n+1, total - s+1)
        
        if mode == 1:
            s = lst[0]
            for i in lst[1:]:
                s -= i
            if length ==0 and s == total:
                return lst
            elif length == 0:
                return []
            elif s <= total:
                return []
            m2 = max(n+1, s-total+1)

        if mode == 3:
            s = lst[0]
            for i in lst[1:]:
                s = s*i
            if length ==0 and s == total:
                return lst
            elif length == 0:
                return []
            elif s > total:
                return []
            m2 =  max(n+1, total - s+1)

        if mode == 2:
            s = lst[0]
            for i in lst[1:]:
                if s % i != 0:
                    return []
                s = s/i
            if length ==0 and s == total:
                return lst
            elif length == 0:
                return []
            elif s < total:
                return []
            m2 =  max(n+1, s+1)

    
    for i in range(m1,m2):
        lst2 = lst + [i]
        ans = cage_helper(length-1, mode, total, n, lst2) 
        if ans != []:
            if type(ans[0]) == list:
                sat = sat + ans
            else:
                sat.append(ans)
    return sat

if __name__ == '__main__':
    funpuzz_grid = [[4]]
    print(funpuzz_csp_model(funpuzz_grid))
    v = Variable("a",[1,2,3])



