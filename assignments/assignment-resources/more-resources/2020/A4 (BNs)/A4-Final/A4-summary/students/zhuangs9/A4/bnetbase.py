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
       It serves as a convienent place to store all of the factors and variables associated
       with a Bayes Net in one place. It also has some utility routines to, e.g,., find
       all of the factors a variable is involved in. 

    '''

import itertools
import collections

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

    Note that if the factor's scope is empty it is a constant factor
    that stores only one value. add_values would be passed something
    like [[0.25]] to set the factor's single value. The get_value
    functions will still work.  E.g., get_value([]) will return the
    factor's single value. Constant factors might be created when a
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
    '''return a new factor that is the product of the factors in Factors '''
     #IMPLEMENT
    if len(Factors) == 1:
        new_scope = Factors[0].get_scope()
        new_var_values = []
        for var in new_scope:
            new_var_values.append(var.dom)
        all_combos = list(itertools.product(*new_var_values))
        new_values = []
        for combo in all_combos:
            new_values.append(list(combo) + [Factors[0].get_value(list(combo))])
        new_factor = Factor('new factor', new_scope)
        new_factor.add_values(new_values)
        return new_factor
    elif len(Factors) == 2:
        new_factor = multi_two(Factors[0], Factors[1])
        # return new factor
        return new_factor
    else:
        new_factors = [multi_two(Factors[0], Factors[1])]
        new_factors += Factors[2:]
        return multiply_factors(new_factors)


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    #IMPLEMENT
    if len(f.scope) == 1:
        new_factor = Factor("constant restricted factor", [])
        new_factor.values = f.values
        return new_factor
    else:
        new_scope = f.get_scope()
        # new_scope.remove(var)
        new_factor = Factor("restricted factor", new_scope)
        new_values = []
        # get all the combinations with var = value in this factor
        var_lists = []

        for f_var in new_scope:
            # if f_var.name == var.name:
            #     f_var.dom = [value]
            var_lists.append(f_var.dom)
        # print(var_lists)
        # get all possible combinations of var lists
        all_combos = list(itertools.product(*var_lists))
        # print(all_combos)
        # f.print_table()
        # print(f.get_value(['g', 's']))
        for combo in all_combos:
            if value in combo:
                new_values.append(list(combo) + [f.get_value(list(combo))])
        # print(new_values)

        # for comb in all_combos:
        #     if value not in comb:
        #         new_values.remove(list(comb))
            # new_factor.add_value_at_current_assignment(f.get_value(comb))
        # for f_var in new_scope:
        #     if f_var.name == var.name:
        #         f_var.dom = [value]
        # print(new_values)
        new_factor.add_values(new_values)
        # new_factor.print_table()
        return new_factor


def multi_two(factor1, factor2):
    # get union of the scopes of all the factors
    table_1 = []
    table_2 = []
    vars_1 = []
    vars_2 = []
    new_scope = []
    new_var_values = []
    new_values = []

    for scope in factor1.get_scope():
        if scope not in new_scope:
            new_scope.append(scope)
    for scope in factor2.get_scope():
        if scope not in new_scope:
            new_scope.append(scope)
    for var in new_scope:
        new_var_values.append(var.dom)
    # print(new_scope)
    all_combo = list(itertools.product(*new_var_values))
    # get all possibility combinations of values given new scope

    # get CPT for 1
    for var in factor1.get_scope():
        vars_1.append(var.dom)
    all_combo_1 = list(itertools.product(*vars_1))
    for combo in all_combo_1:
        table_1.append([factor1.get_value(list(combo))] + list(combo))

    # get CPT for 2
    for var in factor2.get_scope():
        vars_2.append(var.dom)
    all_combo_1 = list(itertools.product(*vars_2))
    for combo in all_combo_1:
        table_2.append([factor2.get_value(list(combo))] + list(combo))

    # initialize new factor
    new_factor = Factor('new factor', new_scope)
    # get product of factors
    # product of table 1 and table 2
    for combo1 in table_1:
        for combo2 in table_2:
            product_value = combo1[0] * combo2[0]
            union_combo = tuple(collections.OrderedDict.fromkeys(combo1[1:] + combo2[1:]))
            # if union of table 1 and table 2 is found in all_combo add to new_values
            if union_combo in all_combo:
                new_values.append(list(union_combo) + [product_value])
    # add to new factors
    new_factor.add_values(new_values)
    # return new factor
    return new_factor

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the summing out of Var'''
    #IMPLEMENT
    # sum up the values of each object in var's domain (ex. sum of all values of 'heavy' and all those for 'light')
    new_scope = []
    new_values = []
    new_val_dict = {}
    if len(f.get_scope()) == 1:
        new_factor = Factor('sum out new factor', f.get_scope())
        new_vars = var.dom
        sum_out = 0
        for value in new_vars:
            sum_out += f.get_value([value])
        for value in new_vars:
            new_values.append([value] + [sum_out])
        new_factor.add_values(new_values)
        return new_factor
    else:
        # get all possible combos without var
        old_vars = []
        for variable in f.get_scope():
            if variable != var:
                new_scope.append(variable)
            old_vars.append(variable.dom)
        all_old_combos = list(itertools.product(*old_vars))
        all_values = []
        for combo in all_old_combos:
            all_values.append(list(combo) + [f.get_value(list(combo))])
        for combo in all_values:
            new_combo = tuple([item for item in combo[:-1] if item not in var.dom])
            if new_combo in new_val_dict.keys():
                new_val_dict[new_combo] += combo[-1]
            else:
                new_val_dict[new_combo] = combo[-1]

        for key in new_val_dict:
            new_values.append(list(key) + [new_val_dict[key]])
        new_factor = Factor('sum out factor', new_scope)
        new_factor.add_values(new_values)
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
    new_factors = Net.factors()
    evidence = []
    for var in EvidenceVars:
        evidence.append([var] + [var.get_evidence()])

    # # restricting
    for i in range(len(new_factors)):
        # replace each factor f in net_factors that mentions a variable(s) in EvidenceVars
        # with its restriction f E = e (might yield constant factor)
        for var in evidence:
            if var[0] in new_factors[i].get_scope():
                # get restriction
                restrict = restrict_factor(new_factors[i], var[0], var[1])
                new_factors[i] = restrict

    # for each remaining vars Z, eliminate:
    # get the remaining vars
    remain_var = min_fill_ordering(new_factors, QueryVar)
    # for each remaining var
    for var in remain_var:
        # compute new factor
        multi_f = []
        for f in new_factors:
            if var in f.get_scope():
                multi_f.append(f)
        # compute the new factor by multiplying factors then summing out
        new_f = multiply_factors(multi_f)
        new_f_sum = sum_out_variable(new_f, var)

        # remove the factors that mention var from new_factors and add new_f_sum to new_factors
        for f in multi_f:
            new_factors.remove(f)
        #add new factor
        new_factors.append(new_f_sum)
        # remain_var = remain_var[1:]
    # remaining factors at the end of process will refer only to query variable Q

    # take product and normalize
    prod = multiply_factors(new_factors)
    return normalize(prod.values)


