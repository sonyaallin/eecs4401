#Look for #IMPLEMENT tags in this file.

'''
Construct and return Kenken CSP model.
'''

from cspbase import *
from propagators import *
import itertools

#example=[[11,21,3,0],[12,22,2,1],[13,23,33,6,3],[31,32,5,0]]
#N=3
#example=[[11,21,4,1],[12,13,2,2],[14,24,1,1],[15,25,1,1],[22,23,9,0],[31,32,3,1],[33,34,44,6,3],[35,45,9,0],[41,51,7,0],[42,43,3,1],[52,53,6,3],[54,55,4,1]]
#N=5
#Vars = []
def kenken_csp(kenken_grid):
    '''
    Kenken
    '''
    Vars = []
    N = kenken_grid[0][0]
    example = kenken_grid[1:]
    domain = []
    for i in range(1,N+1):
        domain.append(i)#domain for each variable
    #VARIABLES
    for i in range(1,N+1):
        for j in range(1,N+1):
            var = Variable("V{}{}".format(i, j))#create variable
            Vars.append(var)
            var.add_domain_values(domain)
    #CONSTRAINTS       
    constraint_list = []
    #binary diff-constraints
    bin_sat_tuples = []
    for i in range(1,N+1):#create tuple list (same for every binary diff-constraint)
        for j in range(1,N+1):
            if i == j:
                continue
            bin_sat_tuples.append((i,j))
    #diff-constraints
    for i in range(0,N):
        for j in range(0,N):
            #row diff-constraints
            for k in range(j+1,N):
                c = Constraint("NE({}{})".format(Vars[i*N+j].name, Vars[i*N+k].name),
                           [Vars[i*N+j], Vars[i*N+k]])
                c.add_satisfying_tuples(bin_sat_tuples)
                constraint_list.append(c)
            #col diff-constraints
            for l in range(i+1,N):
                c = Constraint("NE({}{})".format(Vars[i*N+j].name, Vars[l*N+j].name),
                           [Vars[i*N+j], Vars[l*N+j]])
                c.add_satisfying_tuples(bin_sat_tuples)
                constraint_list.append(c)
    #cage constraints
    for cage in example:
        if len(cage) > 2:
            operator = cage[len(cage)-1]
            target = cage[len(cage)-2]
            #create satisfying tuples
            if operator == 0:
                sat_tuples = addition_tuples(N,target,len(cage)-2)
            elif operator == 1:
                sat_tuples = subtraction_tuples(N,target,len(cage)-2)
            elif operator == 2:
                sat_tuples = div_tuples(N,target,len(cage)-2)
            elif operator == 3:
                sat_tuples = multi_tuples(N,target,len(cage)-2)
            #create constraint
            const_vars = []
            for v in range(0,len(cage)-2):#get vars in cage
                var_name = cage[v]
                var_i = var_name // 10
                var_j = var_name % 10
                #print(var_i,var_j)
                const_vars.append(Vars[(var_i-1)*N+(var_j-1)])
            c = Constraint("CG{}".format(example.index(cage)+1),const_vars)
            c.add_satisfying_tuples(sat_tuples)
            constraint_list.append(c)
    #CSP
    csp = CSP("Kenken",Vars)
    for c in constraint_list:
       csp.add_constraint(c)
    #create var array
    var_array = []
    for i in range(0,N):
        row = []
        for j in range(0,N):
            row.append(Vars[i*N+j])
        var_array.append(row)
    return csp,var_array
    
def addition_tuples(N,target, num_of_vars):
    sat_tups = []
    #generate tuples
    for tup in itertools.product(range(1,N+1),repeat=num_of_vars):
        if sum(tup) == target:#check if constraint is satisfied
            sat_tups.append(tup)
    return sat_tups

def subtraction_tuples(N,target, num_of_vars):
    sat_tups = []
    #generate tuples
    for tup in itertools.product(range(1,N+1),repeat=num_of_vars):
        for perm in itertools.permutations(tup,num_of_vars):
            result = perm[0]
            i = 1
            while(i < num_of_vars):
                result -= perm[i]
                i += 1
            if result == target:
                sat_tups.append(tup)
                break
    return sat_tups

def multi_tuples(N,target, num_of_vars):
    sat_tups = []
    #generate tuples
    for tup in itertools.product(range(1,N+1),repeat=num_of_vars):
        prod = 1
        for val in tup:
            prod *= val
        if prod == target:#check if constraint is satisfied
            sat_tups.append(tup)
    return sat_tups

def div_tuples(N,target, num_of_vars):
    sat_tups = []
    #generate tuples
    for tup in itertools.product(range(1,N+1),repeat=num_of_vars):
        for perm in itertools.permutations(tup,num_of_vars):
            result = perm[0]
            i = 1
            while(i < num_of_vars):
                result //= perm[i]
                i += 1
            if result == target:
                sat_tups.append(tup)
                break
    return sat_tups

