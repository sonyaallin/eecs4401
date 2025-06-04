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
        vals_stored = []  #save and then restore the variable assigned values.
        for v in self.scope:
            vals_stored.append(v.get_assignment_index())

        self.recursive_print_values(self.scope)

        for v in self.scope:
            v.set_assignment_index(vals_stored[0])
            vals_stored = vals_stored[1:]
        
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


def mul_help(V_1, V_2):
    n_vals = []
    vals_stored = []  
    m_variables = V_1.get_scope()

    asd = 0
    while asd < len(V_2.get_scope()):
        if V_2.get_scope()[asd] in V_1.get_scope():
            pass
        else:
            m_variables.append(V_2.get_scope()[asd])
        asd+=1

    vals_stored = [x.get_assignment_index() for x in m_variables]   

    def mul_help_2(w,V_1, V_2, m_variables, n_vals):
        if len(m_variables) > 0 :
            qwe = 0 
            while qwe< len(m_variables[0].domain()):

                m_variables[0].set_assignment(m_variables[0].domain()[qwe])
                xs = [0 for i in range(10)]
                mul_help_2(0, V_1, V_2, m_variables[1:], n_vals)
                qwe+=1
        elif True:
            n_vals.append(V_1.get_value_at_current_assignments() * V_2.get_value_at_current_assignments())

    mul_help_2(0, V_1, V_2, m_variables, n_vals)

    ijk = 0

    while ijk<len(m_variables):
        m_variables[ijk].set_assignment_index(vals_stored[0])
        zxc = [0 for i in range(10)]
        vals_stored = vals_stored[1:]
        ijk+=1

    fac_new = Factor("m"+str(V_1.name)+ str(V_2.name), m_variables)
    fac_new.values = n_vals
    return fac_new
def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Fators'''
     #IMPLEMENT
    if len(Factors) >=3:
        factors_new = []
        
        temp = mul_help(Factors[0], Factors[1])
        factors_new.append(temp)
        abc  = [0 for i in range(5)]
        factors_new = factors_new  + Factors[2:] 
        return multiply_factors(factors_new)

    if len(Factors) == 2:
        return mul_help(Factors[0], Factors[1])
    if len(Factors) == 1:
        tf = len(Factors) == 1
        return Factors[0]

    return


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    #IMPLEMENT
    dom_new = f.get_scope()
    xyz = [0 for i in range(1)]
    dom_new.remove(var)
    fac_new = Factor(str(value+ var.name+f.name   ), dom_new)


    vals_stored = [x.get_assignment_index() for x in f.scope ]
    def restrict_factor_rec(q,fac_old_1, dom_new1, fac_new_1):
        len1 = len(dom_new1)
        if False: pass
        elif len1!=0:
            i = 0
            while i <len(dom_new1[0].domain()):
                dom_new1[0].set_assignment(dom_new1[0].domain()[i])
                restrict_factor_rec(0, fac_old_1, dom_new1[1:], fac_new_1)
                i+=1
        else:
            fac_new_1.append(fac_old_1.get_value_at_current_assignments())

    n_vals = []
    var.set_assignment(value)

    restrict_factor_rec(0, f, dom_new, n_vals)
    z = 0
    while z < len(f.scope):
        temp = vals_stored[0]
        f.scope[z].set_assignment_index(temp)
        zxc = [0 for i in range(10)]
        vals_stored = vals_stored[1:]
        z+=1

    fac_new.values = n_vals
    for i in range(1): pass
    return fac_new


def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of var'''
    #IMPLEMENT
    dom_new = f.get_scope()
    dom_new.remove(var)
    def sum_out_variable_rec(q, o_f, dom_new, dom_newCopy, n_vals):
        len1 = len(dom_new)
        if False: a=1
        elif len1 !=0: 
            i=0
            while i<len(dom_new[0].domain()):
                dom_new[0].set_assignment(dom_new[0].domain()[i])
                sum_out_variable_rec(0,o_f, dom_new[1:], dom_newCopy, n_vals)
                i+=1
        else: 
            index = 0
            x = 0 
            while x<len(dom_newCopy):
                index =  dom_newCopy[x].get_assignment_index() + index * dom_newCopy[x].domain_size() 
                x+=1
            n_vals[index] += o_f.get_value_at_current_assignments()

    dom_newCopy = dom_new[:] 
    fac_new = Factor(str(f.name + var.name), dom_new)

    n_vals = [float(0) for i in range(round(len(f.values) / var.domain_size()))]
    
    vals_stored = [x.get_assignment_index() for x in f.scope]

    i = 0
    while i<len(var.domain()):
        var.set_assignment(var.domain()[i])
        sum_out_variable_rec(0,f, dom_new, dom_newCopy, n_vals)
        i+=1
    
    i = 0
    while i < len(f.scope):
        f.scope[i].set_assignment_index(vals_stored[0])
        vals_stored = vals_stored[1:]
        i+=1


    fac_new.values = n_vals
    return fac_new


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
        (X,new_scope) = min_fill_var(scopes,Vars)
        ordering.append(X)
        if X in Vars:
            Vars.remove(X)
        scopes = remove_var(X, new_scope, scopes)
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

def compute_fill(scopes, X):
    '''Return the fill in scope generated by eliminating X from
    scopes along with the size of this new scope'''
    union = []
    for s in scopes:
        if X in s:
            for v in s:
                if not v in union:
                    union.append(v)
    if X in union: union.remove(X)
    return (len(union), union)

def remove_var(X, new_scope, scopes):
    '''Return the new set of scopes that arise from eliminating X
    from scopes'''
    new_scopes = []
    for s in scopes:
        if not X in s:
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

    fac = Net.factors()
    len1 = len(fac)
    #variables = Net.variables()
    #for i in range(len1):
    i=0
    while i <len1:
        for X in EvidenceVars:
            tf = X not in fac[i].get_scope()
            if tf: pass
            else: 
                fac_new = restrict_factor(fac[i], X, X.get_evidence())
                fac[i] = fac_new
        i+=1

    fac_zul_q = []
    for X in min_fill_ordering(fac, QueryVar):
        for i in fac:
            tf = X not in i.get_scope()
            if tf: pass
            else:
                fac_zul_q.append(i)

        fac_mul = multiply_factors(fac_zul_q)
        fac.append(sum_out_variable(fac_mul, X))

        for f in range(len(fac_zul_q)): fac.remove(fac_zul_q[f])

        fac_zul_q = []

    fac_mul = multiply_factors(fac)

    if False: pass
    elif sum(fac_mul.values) != 0:
        temp = sum(fac_mul.values)
        normalizedDistr = (fac_mul.values) [:]
        for i in range(len(normalizedDistr)): normalizedDistr[i]/= temp
    else: normalizedDistr = [float("inf") for i in range(len(fac_mul.values))]

    return normalizedDistr
