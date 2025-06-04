from itertools import product

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

    # Base case when the size of the factors list is 1
    if len(Factors) == 1:

        # Get the new scope, the variables in the new scope and the combination of all the variable domains for every var in the new scope
        new_scope = Factors[0].get_scope()
        dom_vars_new_scope = [var.domain() for var in new_scope]
        all_comb = [list(assignment) for assignment in product(*dom_vars_new_scope)]

        # Create the new factor
        new_factor = Factor('new', new_scope)

        # Check to see if the given factor is a constant factor and if so, add its value to the new factor and return
        if len(new_scope) == 0:
            constant_factor_val = Factors[0].get_value([])
            new_factor.add_values([[constant_factor_val]])

            return new_factor

        # Create list that will hold all the new assignments
        new_assignments = []

        # Go through every combination of value assignments for the var domains and append the new assignments along with their value to the new assignments list
        for comb in all_comb:
            curr_assignment_val = Factors[0].get_value(comb)
            new_val = list(comb)
            new_val.append(curr_assignment_val)
            new_assignments.append(new_val)

        # Add all the new assignments to the new factor
        new_factor.add_values(new_assignments)
        
        # Return the new factor
        return new_factor

    # Get scope for the combined factor and all the domains for each variable in this new combined factor
    new_scope = []

    # Create the new scope, checking for duplicate variables
    for factor in Factors:
        for var in factor.get_scope():
            if var not in new_scope:
                new_scope.append(var)

    # Create a list of all the domains for every var 
    var_domain = [var.domain() for var in new_scope]

    # Create the new factor
    new_factor = Factor('new', new_scope)

    # Get the first factor and recurse for the next factor
    first_factor = Factors[0]
    next_factor = multiply_factors(Factors[1:])

    # Check to see if the first and the next factor are constant factors and if so, multiply their values, add it to the new factor and return
    if len(first_factor.get_scope()) == 0 and len(next_factor.get_scope()) == 0:
        first_factor_val = first_factor.get_value([])
        next_factor_val = next_factor.get_value([])
        new_factor.add_values([[first_factor_val * next_factor_val]])

    # Find all combinations of variable domains of all the variables in the new scope
    all_val_comb = [list(assignment) for assignment in product(*var_domain)]
    
    # Go through all combinations of all the var domains
    for comb in all_val_comb:
        val_index = 0

        # Assign each var a value from its domain
        for var in new_scope:
            var.set_assignment(comb[val_index])
            val_index+=1

        # Find the first and second factors values at current assignment and multiply them together, then add the new val for the current assignment to the new factor
        first_factor_curr_val = first_factor.get_value_at_current_assignments()
        next_factor_curr_val = next_factor.get_value_at_current_assignments()
        new_curr_val = first_factor_curr_val * next_factor_curr_val
        new_factor.add_value_at_current_assignment(new_curr_val)
    
    # Return the new factor
    return new_factor


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''

    # Get the scope of the factor, remove the given var from the factor and set the assignment of the given var to the given value
    factor_scope = f.get_scope()
    factor_scope.remove(var)
    var.set_assignment(value)

    # Get all the domains for all the var in the factor scope
    var_domain = [variable.domain() for variable in factor_scope]

    # Find all combinations of variable domains of all the variables in the factor scope
    all_val_comb = [list(assignment) for assignment in product(*var_domain)]

    # Create the new factor
    new_factor = Factor('new', factor_scope)

    # If factor only had one var in its scope, return a constant factor
    if len(factor_scope) == 0:
        new_factor.add_value_at_current_assignment(f.get_value_at_current_assignments())
        return new_factor


    # Go through all combinations of all the var domains
    for comb in all_val_comb:
        val_index = 0

        # Assign each var a value from its domain
        for variable in factor_scope:
            variable.set_assignment(comb[val_index])
            val_index+=1
        
        # Get the value for the currently assignment of values to the vars and add that val to the new factor for the current assignment of values
        new_curr_val = f.get_value_at_current_assignments()
        new_factor.add_value_at_current_assignment(new_curr_val)
   
    # Return the new factor
    return new_factor

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    
    # Get the scope of the factor and remove the given var from the factor
    factor_scope = f.get_scope()
    factor_scope.remove(var)

    # Create the new factor
    new_factor = Factor('new', factor_scope)

    # If factor only had one var in its scope, return a constant factor
    if len(factor_scope) == 0:
        new_value = 0

        # Go through all the values in the domain of the variable that is being summed out
        for val in var.domain():
            
            # Assign a val to the variable that is being summed out
            var.set_assignment(val)
            # Get the value for the currently assignment of values to the vars and increment new_value by that value
            new_value += f.get_value_at_current_assignments()

        # Add to the new factor the new value for the current assignment of variables
        new_factor.add_value_at_current_assignment(new_value)

        # Return the new factor
        return new_factor

    # Get all the domains for all the var in the factor scope
    var_domain = [variable.domain() for variable in factor_scope]

    # Find all combinations of variable domains of all the variables in the factor scope
    all_val_comb = [list(assignment) for assignment in product(*var_domain)]

     # Go through all combinations of all the var domains
    for comb in all_val_comb:
        val_index = 0

        # Assign each var in the new factor scope a value from its domain
        for variable in factor_scope:
            variable.set_assignment(comb[val_index])
            val_index+=1
        
        # Initilize the new value that is going to be added to the new factor
        new_value = 0

        # Go through all the values in the domain of the variable that is being summed out
        for val in var.domain():
            
            # Assign a val to the variable that is being summed out
            var.set_assignment(val)
            # Get the value for the currently assignment of values to the vars and increment new_value by that value
            new_value += f.get_value_at_current_assignments()

        # Add to the new factor the new value for the current assignment of variables
        new_factor.add_value_at_current_assignment(new_value)

    # Return the new factor
    return new_factor

def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''

    # If sum of nums is 0, then return a list of 0s
    if sum(nums) == 0:
        return [0 for num in nums]

    # Divide each number by the sum of all the numbers in nums
    normalized = [float(num)/sum(nums) for num in nums]

    # Return the normalized list of numbers
    return normalized

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

    # Get the BN factors list
    bn_factors = Net.factors()

    # Get the remaining var list with the Query and Evidence Vars removed
    Z = Net.variables()
    Z.remove(QueryVar)
    for var in EvidenceVars:
        Z.remove(var)

    # Go through the Evidence Vars and restrict each factor in bn_factors by each var in Evidence Vars and its value
    for var in EvidenceVars:

        # Go through each factor in bn_factors and if the current var in Evidence Var is in the factor, 
        # restrict that factor by the Evidence Var and its value and replace the factor in the factors list
        # with the new restricted factor
        for factor_i in range(len(bn_factors)):
            if var in bn_factors[factor_i].get_scope():
                bn_factors[factor_i] = restrict_factor(bn_factors[factor_i], var, var.get_evidence())

    # Go through every var in Z and take the product of every factor that includes the var 
    for var in Z:

        # Initlize the factors product list
        g_factor_product_list = []

        # Go through every factor in bn factors and if the current var is in its scope, add that factor to the factor product list
        for factor in bn_factors:
            if var in factor.get_scope():
                g_factor_product_list.append(factor)

        # Get the new factor which is a product of all the factors in bn factors that include the current var in Z.
        # These are all the factors added to the factor product list. Then sum out the current var in Z from this new factor
        new_factor_g = multiply_factors(g_factor_product_list)
        new_factor_g = sum_out_variable(new_factor_g, var)

        # Remove all the factors in bn factors that mention the current var in Z, which are also all the factors that are currently
        # in the factor product list
        for factor in g_factor_product_list:
            bn_factors.remove(factor)

        # Append the new factor, which is a product of previous factors and has been summed out, to the bn factors list
        bn_factors.append(new_factor_g)


    # Get the final factor by taking the product of all the factors in the bn factors list and also initialize the list of unnormalized values
    final_factor = multiply_factors(bn_factors)
    unnormalized_values = []

    # Set the assignment of each var to its evidence value
    for var in EvidenceVars:
        var.set_assignment(var.get_evidence())

    # Go through all the values in our Query Var domain and assign the val to the Query Val, then get the unnormalized value for the current assignment
    # of this var (which is the only var in the scope of the new factor), in the new factor and append the unnormalized value to the unnormalized values list
    for val in QueryVar.domain():
        QueryVar.set_assignment(val)
        unnormalized_values.append(final_factor.get_value_at_current_assignments())

    # Get the normalized values list and return this list
    normalized_values = normalize(unnormalized_values)
    return normalized_values
    
