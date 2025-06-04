'''Classes for variable elimination Routines 
   A) class BN_Variable

      This class allows one to define Bayes Net variables.

      On initialization the variable object can be given a name and a
      domain of values. This list of domain values can be added to or
      deleted from in support of an incremental specification of the
      variable domain.

      The variable also has a set and get value method. These set a
      value for the variable that can be used by the factor class. 


    B) class factor

      This class allows one to define a factor specified by a table
      of values. 

      On initialization the variables the factor is over is
      specified. This must be a list of variables. This list of
      variables cannot be changed once the constraint object is
      created.

      Once created the factor can be incrementally initialized with a
      list of values. To interact with the factor object one first
      sets the value of each variable in its scope (using the
      variable's set_value method), then one can set or get the value
      of the factor (a number) on those fixed values of the variables
      in its scope.

      Initially, one creates a factor object for every conditional
      probability table in the bayes-net. Then one initializes the
      factor by iteratively setting the values of all of the factor's
      variables and then adding the factor's numeric value using the
      add_value method. 

    C) class BN
       This class allows one to put factors and variables together to form a Bayes net.
       It serves as a convient place to store all of the factors and variables associated
       with a Bayes Net in one place. It also has some utility routines to, e.g,., find
       all of the factors a variable is involved in. 

    '''

class Variable:
    '''Class for defining Bayes Net variables. '''
    
    def __init__(self, name, domain=[]):
        '''Create a variable object, specifying its name (a
        string). Optionally specify the initial domain.
        '''
        self.name = name                #text name for variable
        self.dom = list(domain)         #Make a copy of passed domain
        self.evidence_index = 0         #evidence value (stored as index into self.dom)
        self.assignment_index = 0       #For use by factors. We can assign variables values
                                        #and these assigned values can be used by factors
                                        #to index into their tables.

    def add_domain_values(self, values):
        '''Add domain values to the domain. values should be a list.'''
        for val in values: self.dom.append(val)

    def value_index(self, value):
        '''Domain values need not be numbers, so return the index
           in the domain list of a variable value'''
        return self.dom.index(value)

    def domain_size(self):
        '''Return the size of the domain'''
        return(len(self.dom))

    def domain(self):
        '''return the variable domain'''
        return(list(self.dom))

    def set_evidence(self,val):
        '''set this variable's value when it operates as evidence'''
        self.evidence_index = self.value_index(val)

    def get_evidence(self):
        return(self.dom[self.evidence_index])

    def set_assignment(self, val):
        '''Set this variable's assignment value for factor lookups'''
        self.assignment_index = self.value_index(val)

    def get_assignment(self):
        return(self.dom[self.assignment_index])

    ##These routines are special low-level routines used directly by the
    ##factor objects
    def set_assignment_index(self, index):
        '''This routine is used by the factor objects'''
        self.assignment_index = index

    def get_assignment_index(self):
        '''This routine is used by the factor objects'''
        return(self.assignment_index)

    def __repr__(self):
        '''string to return when evaluating the object'''
        return("{}".format(self.name))
    
    def __str__(self):
        '''more elaborate string for printing'''
        return("{}, Dom = {}".format(self.name, self.dom))


class Factor: 

    '''Class for defining factors. A factor is a function that is over
    an ORDERED sequence of variables called its scope. It maps every
    assignment of values to these variables to a number. In a Bayes
    Net every CPT is represented as a factor. Pr(A|B,C) for example
    will be represented by a factor over the variables (A,B,C). If we
    assign A = a, B = b, and C = c, then the factor will map this
    assignment, A=a, B=b, C=c, to a number that is equal to Pr(A=a|
    B=b, C=c). During variable elimination new factors will be
    generated. However, the factors computed during variable
    elimination do not necessarily correspond to conditional
    probabilities. Nevertheless, they still map assignments of values
    to the variables in their scope to numbers.

    Note that if the factor's scope is empty it is a constaint factor
    that stores only one value. add_values would be passed something
    like [[0.25]] to set the factor's single value. The get_value
    functions will still work.  E.g., get_value([]) will return the
    factor's single value. Constaint factors migth be created when a
    factor is restricted.'''

    def __init__(self, name, scope):
        '''create a Factor object, specify the Factor name (a string)
        and its scope (an ORDERED list of variable objects).'''
        self.scope = list(scope)
        self.name = name
        size = 1
        for v in scope:
            size = size * v.domain_size()
        self.values = [0]*size  #initialize values to be long list of zeros.

    def get_scope(self):
        '''returns copy of scope...you can modify this copy without affecting 
           the factor object'''
        return list(self.scope)

    def add_values(self, values):
        '''This routine can be used to initialize the factor. We pass
        it a list of lists. Each sublist is a ORDERED sequence of
        values, one for each variable in self.scope followed by a
        number that is the factor's value when its variables are
        assigned these values. For example, if self.scope = [A, B, C],
        and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
        C.domain() = ['heavy', 'light'], then we could pass add_values the
        following list of lists
        [[1, 'a', 'heavy', 0.25], [1, 'a', 'light', 1.90],
         [1, 'b', 'heavy', 0.50], [1, 'b', 'light', 0.80],
         [2, 'a', 'heavy', 0.75], [2, 'a', 'light', 0.45],
         [2, 'b', 'heavy', 0.99], [2, 'b', 'light', 2.25],
         [3, 'a', 'heavy', 0.90], [3, 'a', 'light', 0.111],
         [3, 'b', 'heavy', 0.01], [3, 'b', 'light', 0.1]]

         This list initializes the factor so that, e.g., its value on
         (A=2,B=b,C='light) is 2.25'''

        for t in values:
            index = 0
            for v in self.scope:
                index = index * v.domain_size() + v.value_index(t[0])
                t = t[1:]
            self.values[index] = t[0]
         
    def add_value_at_current_assignment(self, number): 

        '''This function allows adding values to the factor in a way
        that will often be more convenient. We pass it only a single
        number. It then looks at the assigned values of the variables
        in its scope and initializes the factor to have value equal to
        number on the current assignment of its variables. Hence, to
        use this function one first must set the current values of the
        variables in its scope.

        For example, if self.scope = [A, B, C],
        and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
        C.domain() = ['heavy', 'light'], and we first set an assignment for A, B
        and C:
        A.set_assignment(1)
        B.set_assignment('a')
        C.set_assignment('heavy')
        then we call 
        add_value_at_current_assignment(0.33)
         with the value 0.33, we would have initialized this factor to have
        the value 0.33 on the assigments (A=1, B='1', C='heavy')
        This has the same effect as the call
        add_values([1, 'a', 'heavy', 0.33])

        One advantage of the current_assignment interface to factor values is that
        we don't have to worry about the order of the variables in the factor's
        scope. add_values on the other hand has to be given tuples of values where 
        the values must be given in the same order as the variables in the factor's 
        scope. 

        See recursive_print_values called by print_table to see an example of 
        where the current_assignment interface to the factor values comes in handy.
        '''

        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        self.values[index] = number

    def get_value(self, variable_values):

        '''This function is used to retrieve a value from the
        factor. We pass it an ordered list of values, one for every
        variable in self.scope. It then returns the factor's value on
        that set of assignments.  For example, if self.scope = [A, B,
        C], and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
        C.domain() = ['heavy', 'light'], and we invoke this function
        on the list [1, 'b', 'heavy'] we would get a return value
        equal to the value of this factor on the assignment (A=1,
        B='b', C='light')'''

        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.value_index(variable_values[0])
            variable_values = variable_values[1:]
        return self.values[index]

    def get_value_at_current_assignments(self):

        '''This function is used to retrieve a value from the
        factor. The value retrieved is the value of the factor when
        evaluated at the current assignment to the variables in its
        scope.

        For example, if self.scope = [A, B, C], and A.domain() =
        [1,2,3], B.domain() = ['a', 'b'], and C.domain() = ['heavy',
        'light'], and we had previously invoked A.set_assignment(1),
        B.set_assignment('a') and C.set_assignment('heavy'), then this
        function would return the value of the factor on the
        assigments (A=1, B='1', C='heavy')'''
        
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        return self.values[index]

    def print_table(self):
        '''print the factor's table'''
        saved_values = []  #save and then restore the variable assigned values.
        for v in self.scope:
            saved_values.append(v.get_assignment_index())

        self.recursive_print_values(self.scope)

        for v in self.scope:
            v.set_assignment_index(saved_values[0])
            saved_values = saved_values[1:]
        
    def recursive_print_values(self, vars):
        if len(vars) == 0:
            print("[",end=""),
            for v in self.scope:
                print("{} = {},".format(v.name, v.get_assignment()), end="")
            print("] = {}".format(self.get_value_at_current_assignments()))
        else:
            for val in vars[0].domain():
                vars[0].set_assignment(val)
                self.recursive_print_values(vars[1:])

    def __repr__(self):
        return("{}".format(self.name))

class BN:

    '''Class for defining a Bayes Net.
       This class is simple, it just is a wrapper for a list of factors. And it also
       keeps track of all variables in the scopes of these factors'''

    def __init__(self, name, Vars, Factors):
        self.name = name
        self.Variables = list(Vars)
        self.Factors = list(Factors)
        for f in self.Factors:
            for v in f.get_scope():     
                if not v in self.Variables:
                    print("Bayes net initialization error")
                    print("Factor scope {} has variable {} that", end='')
                    print(" does not appear in list of variables {}.".format(list(map(lambda x: x.name, f.get_scope())), v.name, list(map(lambda x: x.name, Vars))))

    def factors(self):
        return list(self.Factors)

    def variables(self):
        return list(self.Variables)

def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Fators'''
     #IMPLEMENT
    vs = []
    n = 0
    for factor in Factors:
        
        for v in factor.get_scope():
            vs.append(v)
            vs = list(dict.fromkeys(vs))


    r = Factor(name = '*', scope = vs)
    asigns = pull(vs)
    
    for a in asigns:
        for i in range(len(vs)):
            vs[i].set_assignment(a[i])

        mul = 1
        for factor in Factors:
            value = factor.get_value_at_current_assignments()
            mul *=  value
            
        r.add_value_at_current_assignment(mul)
    return r

def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    #IMPLEMENT
    var.set_assignment(value)
    vs = f.get_scope()
    vs.remove(var)
    
    r = Factor(name = 'r', scope = vs)
    assigns =pull(vs)
   
    for a in assigns:
        for i in range(len(vs)):
            vs[i].set_assignment(a[i])
        
        val = f.get_value_at_current_assignments()
        r.add_value_at_current_assignment(val)
    
    return r

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    #IMPLEMENT
    vs = f.get_scope()
    vs.remove(var)
    
    r= Factor(name = '+', scope = vs)
    assigns = pull(vs)
    
    for a in assigns:
    
        for i in range(len(vs)):
            vs[i].set_assignment(a[i])
        
        add = 0
        for vd in var.domain():
            var.set_assignment(vd)
            value = f.get_value_at_current_assignments()
            add += value
        
        r.add_value_at_current_assignment(add)
    return r

def normalize(nums): 
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''    
    #IMPLEMENT
    r = []
    if sum(nums) == 0:
        
        for i in range(len(nums)):
            r.append(0)
            
    else:
        for num in nums:
            r.append((num/sum(nums)))
    
    return r



def pull(v): #working
    r = []
    length =  len(v)
    n = 0
    
    if length != 0:
        n+= 1
        v1 = v[0]
        v_rest = pull(v[1:]) #recursive back 
        v1_dom = v1.domain()
        
        for v1_amt  in v1_dom:
            for par in v_rest: #
                combine = [v1_amt] + par
                r.append(combine)
        
        return r
    else:
        
        return [[]]



###Orderings
def min_fill_ordering(Factors, QueryVar):
    '''Compute a min fill ordering given a list of factors. Return a list
    of variables from the scopes of the factors in Factors. The QueryVar is 
    NOT part of the returned ordering'''
    scopes = []
    for f in Factors:
        scopes.append(list(f.get_scope()))
    Vars = []
    for s in scopes:
        for v in s:
            if not v in Vars and v != QueryVar:
                Vars.append(v)
    
    ordering = []
    while Vars:
        (var,new_scope) = min_fill_var(scopes,Vars)
        ordering.append(var)
        if var in Vars:
            Vars.remove(var)
        scopes = remove_var(var, new_scope, scopes)
    return ordering

def min_fill_var(scopes, Vars):
    '''Given a set of scopes (lists of lists of variables) compute and
    return the variable with minimum fill in. That the variable that
    generates a factor of smallest scope when eliminated from the set
    of scopes. Also return the new scope generated from eliminating
    that variable.'''
    minv = Vars[0]
    (minfill,min_new_scope) = compute_fill(scopes,Vars[0])
    for v in Vars[1:]:
        (fill, new_scope) = compute_fill(scopes, v)
        if fill < minfill:
            minv = v
            minfill = fill
            min_new_scope = new_scope
    return (minv, min_new_scope)

def compute_fill(scopes, var):
    '''Return the fill in scope generated by eliminating var from
    scopes along with the size of this new scope'''
    union = []
    for s in scopes:
        if var in s:
            for v in s:
                if not v in union:
                    union.append(v)
    if var in union: union.remove(var)
    return (len(union), union)

def remove_var(var, new_scope, scopes):
    '''Return the new set of scopes that arise from eliminating var
    from scopes'''
    new_scopes = []
    for s in scopes:
        if not var in s:
            new_scopes.append(s)
    new_scopes.append(new_scope)
    return new_scopes
            
        
###
def VE(Net, QueryVar, EvidenceVars):
    '''
    Input: Net---a BN object (a Bayes Net)
           QueryVar---a Variable object (the variable whose distribution
                      we want to compute)
           EvidenceVars---a LIST of Variable objects. Each of these
                          variables has had its evidence set to a particular
                          value from its domain using set_evidence. 

   VE returns a distribution over the values of QueryVar, i.e., a list
   of numbers one for every value in QueryVar's domain. These numbers
   sum to one, and the i'th number is the probability that QueryVar is
   equal to its i'th value given the setting of the evidence
   variables. For example if QueryVar = A with Dom[A] = ['a', 'b',
   'c'], EvidenceVars = [B, C], and we have previously called
   B.set_evidence(1) and C.set_evidence('c'), then VE would return a
   list of three numbers. E.g. [0.5, 0.24, 0.26]. These numbers would
   mean that Pr(A='a'|B=1, C='c') = 0.5 Pr(A='a'|B=1, C='c') = 0.24
   Pr(A='a'|B=1, C='c') = 0.26
    '''
    #IMPLEMENT
    fs = Net.factors()
    min_order = min_fill_ordering(fs, QueryVar)
    
    
    for v in min_order:
        
        if v in EvidenceVars: # V is evidence 
            new_fs = []
            for f in fs:
                if v in f.get_scope(): #evidence in f scope 
                    restrict_f = restrict_factor(f, v, v.get_evidence())
                    new_fs.append(restrict_f)
                else:
                    new_fs.append(f)
            
            fs = new_fs #reduced factors 
            
            
           
        elif v not in EvidenceVars: # V is not edivence 
            new_fs = []
            add = []
            non_add = []
            
            for f in fs:
                if v in f.get_scope(): #evariable in f scope 
                    add.append(f)
                else:
                    non_add.append(f)
            sum_out = sum_out_variable(multiply_factors(add), v)
            non_add.append(sum_out)
            fs = non_add
     
            
    result_factor = multiply_factors(fs)
    prob = []
    
    for amt in QueryVar.domain():
        QueryVar.set_assignment(amt)
        prob.append(result_factor.get_value_at_current_assignments())
    
    normal = normalize(prob)
    return normal

#Questions Code
'''

print('a:')
hl.set_evidence('YES')
print(VE(medical, vg, []))
print(VE(medical, vg, [hl]))
bmi.set_evidence('~28.0')
print(VE(medical, vg, [hl, bmi]))
print(VE(medical, vg, [bmi]))
    

 
print('b:')
l1 = []

for i in medical.Variables:
    new = medical.Variables
    for x in new:
        if x != i:              
            x.set_evidence(x.dom[0])
            for z in new:
                if z != i and z != x:
                    z.set_evidence(z.dom[0])
                    for y in new:
                        if y != i and y != x and y != z:
                            y.set_evidence(y.dom[0])
                            v1 = VE(medical, i, [x,z])
                            v2 = VE(medical, i, [x,z,y])
                            if v1 == v2:
                                for k in new:
                                    if k != i and k != x and k != z and k!=y:
                                        k.set_evidence(k.dom[0])
                                        v3 = VE(medical, i, [y,x,z,k])
                                        if v2 != v3:
                                            l1.append([i,y,k,x,z])
print(l1)

 
def rand_evi(x):
    return x.dom[0]
print(VE(medical, bmi, []))
hl.set_evidence(rand_evi(hl))
vg.set_evidence(rand_evi(vg))
gd.set_evidence(rand_evi(gd))
co.set_evidence(rand_evi(co))
ag.set_evidence(rand_evi(ag))
print(VE(medical, bmi, [hl,co]))

print(VE(medical, bmi, [hl,co,vg]))

print(VE(medical, bmi, [hl,co,vg,ag]))




###################################
print('Q3:')
l1 = []
for i in medical.Variables:
    v0 = VE(medical, i, [])
    new = medical.Variables
    for x in new:
        if x != i:
            for dom1 in x.dom:           
                x.set_evidence(dom1)
                v1 = VE(medical, i, [x])
                ########################
                if v1[0] < v0[0]:
                    for y in new:
                        if y != i and y != x :
                            for dom2 in y.dom:             
                                y.set_evidence(dom2)
                                v2 = VE(medical, i, [x,y])
                                #########################
                                if v2[0] <v1[0]:
                                    for z in new:
                                        if z != i and z != x and z != y:
                                            for dom3 in z.dom:             
                                                z.set_evidence(dom3)
                                                v3 = VE(medical, i, [x,y,z])
                                                #########################
                                                if v3[0] <v2[0]:
                                                    for a in new:
                                                        if a != i and a != x and a != y and a !=z:
                                                            for dom4 in a.dom:             
                                                                a.set_evidence(dom4)
                                                                v4 = VE(medical, i, [x,y,z,a])
                                                                #########################
                                                                if v4[0] <v3[0]:
                                                                    for b in new:
                                                                        if b != i and b != x and b != y and b !=z and b!=a:                               
                                                                            for dom5 in b.dom:             
                                                                                b.set_evidence(dom5)
                                                                                v5 = VE(medical, i, [x,y,z,a,b])
                                                                                #################################
                                                                                if v5[0]<v4[0]:
                                                                                    l1.append([i,[x,dom1],[y,dom2],[z,dom3],[a,dom4],[b,dom5]])
print(l1)
                  
co.set_evidence('YES')
rg.set_evidence('City')
hl.set_evidence('YES')
ac.set_evidence('Insufficient')
ag.set_evidence('~60')
print(VE(medical, bmi, []))
print(VE(medical, bmi, [co]))
print(VE(medical, bmi, [co,rg]))
print(VE(medical, bmi, [co,rg,ag]))
print(VE(medical, bmi, [co,rg,ag,ac]))
print(VE(medical, bmi, [co,rg,ag,ac,hl]))


print('Q4:')

l1 = []
for i in medical.Variables:
    v0 = VE(medical, i, [])
    new = medical.Variables
    for x in new:
        if x != i:
            for dom1 in x.dom:           
                x.set_evidence(dom1)
                v1 = VE(medical, i, [x])
                ########################
                if v1[0] > v0[0]:
                    for y in new:
                        if y != i and y != x :
                            for dom2 in y.dom:             
                                y.set_evidence(dom2)
                                v2 = VE(medical, i, [x,y])
                                #########################
                                if v2[0] > v1[0]:
                                    for z in new:
                                        if z != i and z != x and z != y:
                                            for dom3 in z.dom:             
                                                z.set_evidence(dom3)
                                                v3 = VE(medical, i, [x,y,z])
                                                #########################
                                                if v3[0] >v2[0]:
                                                    for a in new:
                                                        if a != i and a != x and a != y and a !=z:
                                                            for dom4 in a.dom:             
                                                                a.set_evidence(dom4)
                                                                v4 = VE(medical, i, [x,y,z,a])
                                                                #########################
                                                                if v4[0] >v3[0]:
                                                                    for b in new:
                                                                        if b != i and b != x and b != y and b !=z and b!=a:                               
                                                                            for dom5 in b.dom:             
                                                                                b.set_evidence(dom5)
                                                                                v5 = VE(medical, i, [x,y,z,a,b])
                                                                                #################################
                                                                                if v5[0]>v4[0]:
                                                                                    l1.append([i,[x,dom1],[y,dom2],[z,dom3],[a,dom4],[b,dom5]])
                                                                                
                                                                                if len(l1) > 10:
                                                                                    break

                                                                                       

hl.set_evidence('NO')
db.set_evidence('NO')
ac.set_evidence('Sufficient')
ht.set_evidence('NO')
co.set_evidence('NO')
print(VE(medical, bmi, []))
print(VE(medical, bmi, [hl]))
print(VE(medical, bmi, [hl,db]))
print(VE(medical, bmi, [hl,db,ac]))
print(VE(medical, bmi, [hl,db,ac,ht]))
print(VE(medical, bmi, [hl,db,ac,ht,co]))


print('part3')
print(VE(medical, ht, []))
hl.set_evidence('YES')
db.set_evidence('YES')
gd.set_evidence('Male')
print(VE(medical, ht, [hl,db]))
print(VE(medical, ht, [hl,db,gd]))

print('part3')
l1 = []

l1 = []
for i in medical.Variables:
    new = medical.Variables
    for x in new:
        if x != i :
            for dom1 in x.dom:              
                x.set_evidence(dom1)
                for y in new:
                    if y != i and y != x :
                        for dom3 in y.dom: 
                            y.set_evidence(dom3)
                            v1 = VE(medical, i, [x,])
                            v2 = VE(medical, i, [y,x,])
                            if v1 == v2:
                                if [i,x,y] not in l1:
                                    l1.append([i,x,y])
                                            

print(l1)



rg.set_evidence('Countryside')
hl.set_evidence('YES')
gd.set_evidence('Male')

#print(VE(medical, rg, [hl]))
#print(VE(medical, rg, [hl,gd]))
print('\n')
#print(VE(medical, hl, [rg]))
print(VE(medical, hl, [rg,gd]))
'''
