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
    
#implemented
def multiply_factors(Factors):

    #case if only multiplying one factor
    if len(Factors) == 1:
        return Factors[0]
    
    #case if only multiplying 2 factors
    elif len(Factors) == 2:
        fact1 = Factors[0]
        fact2= Factors[1]    
        new_vals = []
        s_values = []         
        new_name = fact1.name + "x" + fact2.name
        merged_vars = fact1.get_scope()
        for var in fact2.get_scope():
            if var not in fact1.get_scope():
                merged_vars.append(var)
        new_factor = Factor(new_name, merged_vars)
 
        for i in merged_vars:
            s_values.append(i.get_assignment_index())
        t=1
        pf=0
        recurs_helper(fact1,fact2,pf, merged_vars, 0, new_vals, t)
        for i in merged_vars:
            i.set_assignment_index(s_values[0])
            s_values = s_values[1:]
    
        new_factor.values = new_vals
        return new_factor       

    else:
        fact1 = Factors[0]
        fact2= Factors[1]         
        new_factors = []
        
        new_name = fact1.name + "x" + fact2.name
        merged_vars = fact1.get_scope()
        for v in fact2.get_scope():
            if v not in fact1.get_scope():
                merged_vars.append(v)
        new_factor = Factor(new_name, merged_vars)
        new_vals = []
        s_values = []  
        
        for v in merged_vars:
            s_values.append(v.get_assignment_index())
        t=1
        pf=0
        recurs_helper(fact1,fact2,pf, merged_vars,0, new_vals, t)
        for i in merged_vars:
            i.set_assignment_index(s_values[0])
            s_values = s_values[1:]
        new_factor.values = new_vals
        
        new_factors.append(new_factor)
        new_factors += Factors[2:]
        return multiply_factors(new_factors)   
    
#implemented
def restrict_factor(fact, var, val):
    
    new_name = "( " + fact.name + " restricted on " + var.name + " , " + val + " )"
    new_scope = fact.get_scope()
    new_scope.remove(var)
    new_factor = Factor(new_name, new_scope)
    newvals = []
    s_vals = []  
    for i in fact.scope:
        s_vals.append(i.get_assignment_index())
    var.set_assignment(val)
    f1=0
    f2=0
    t=0
    nsc=0
    recurs_helper(f1,f2,fact,new_scope,nsc,newvals,t)
    for i in fact.scope:
        i.set_assignment_index(s_vals[0])
        saved_values = s_vals[1:]
    new_factor.values = newvals
    #return restricted factor
    return new_factor

#helper implemented
def recurs_helper(f1,f2, pf, nsmv,nsc, nv, t):
    #use case 1
    if t == 0:
        if len(nsmv) == 0:
            nv.append(pf.get_value_at_current_assignments())
        else:
            i=0
            while i< len(nsmv[0].domain()):
                val = nsmv[0].domain()[i]        
                nsmv[0].set_assignment(val)
                recurs_helper(f1,f2,pf, nsmv[1:],nsc, nv,t)
                i+=1
    #use case 2
    elif t == 1:
        if len(nsmv) == 0:
            nv.append(f1.get_value_at_current_assignments() * f2.get_value_at_current_assignments())
        else:
            i=0
            while i< len(nsmv[0].domain()):
                val = nsmv[0].domain()[i]
                nsmv[0].set_assignment(val)
                recurs_helper(f1,f2,pf,nsmv[1:],nsc, nv,t)
                i+=1   
    #use case 3
    else: 
        if len(nsmv) == 0:
            accum = 0
            for var in nsc:
                accum = accum * var.domain_size() + var.get_assignment_index()
            nv[accum] += pf.get_value_at_current_assignments()
        else:
            i=0
            while i< len(nsmv[0].domain()):
                val = nsmv[0].domain()[i]            
                nsmv[0].set_assignment(val)
                recurs_helper(f1,f2,pf,nsmv[1:],nsc,nv,t)
                i+=1
                       
#implemented
def sum_out_variable(fact, var):

    new_name = "( " + fact.name + "sum-out with" + var.name + " )"
    new_scope = fact.get_scope()
    new_scope.remove(var)
    new_scopelist = list(new_scope)
    new_factor = Factor(new_name, new_scope)
    newvals_size = round(len(fact.values) / var.domain_size())
    newvals = [0.0] * newvals_size #initialize to list of zeros
    s_vals = [] 
    
    for i in fact.scope:
        s_vals.append(i.get_assignment_index())
    for i in var.domain():
        var.set_assignment(i)
        t=2
        recurs_helper(0,0, fact, new_scope,new_scopelist, newvals, t)
    for i in fact.scope:
        i.set_assignment_index(s_vals[0])
        s_vals = s_vals[1:]
    new_factor.values = newvals
    
    return new_factor


def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''
    s = sum(nums)
    if s == 0:
        newnums = [0]*len(nums)
    else:
        newnums = []
        for n in nums:
            newnums.append(n/s)
    return newnums

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
            
#implemented
def VE(bnet, query, evidence):
        
    factors = bnet.factors()
    var_list = bnet.variables()
    multlist=[]
    i=0
    while i < len(factors):
        for var in evidence:
            if var in factors[i].get_scope():
                newFactor = restrict_factor(factors[i], var, var.get_evidence())   # make assignements for evidence vars
                factors[i] = newFactor
        i+=1
    #min fill ordering
    minfillorder = min_fill_ordering(factors, query)
    
    #fill out list of factors to multiply
    j=0
    while j < len (minfillorder):
        i=minfillorder[j]
        multlist = []
        for fact in factors:
            if i in fact.get_scope():
                multlist.append(fact)
                continue

        mf = multiply_factors(multlist)
        sf = sum_out_variable(mf, i)
        
        
        for f in multlist:
            factors.remove(f)
        factors.append(sf)
        minfillorder = minfillorder[1:]

    # remaining factors
    mf = multiply_factors(factors)
    inf=float('inf') 
    if sum(mf.values) == 0:
        finaldist = [inf * len(mf.values)] #not normalized
    else: 
        finaldist = []
        for i in mf.values:
            finaldist.append(i/sum(mf.values))

    return finaldist
