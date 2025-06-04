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

import itertools

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

    # Accumulator variable for factors
    acc_factor = Factors[0]

    # Multiply every factor with the accumulator
    if len(Factors) > 1:
        for i in range(1, len(Factors)):
            acc_factor = mult_two_factors(acc_factor, Factors[i])

    return acc_factor

def mult_two_factors(factor_one, factor_two):
    '''return a new factor that is the product of the two factors'''

    # Setup for factor scope variables
    factor_one_scope = factor_one.get_scope()
    factor_two_scope = factor_two.get_scope()
    common_vars_lst = list(set(factor_one_scope) & set(factor_two_scope))

    # Variables for identifying common factor variables
    c_var_loc_lst = []
    for c_vars in common_vars_lst:
        c_var_loc_lst.append([factor_one_scope.index(c_vars), factor_two_scope.index(c_vars)])

    # Get a list of all factor variable domains for factor_one
    fac_one_vars_dom_lst = []
    for fac_one_vars in factor_one_scope:
        fac_one_vars_dom_lst.append(fac_one_vars.domain())

    # Get all variable domain combinations for factor_one
    fac_one_prod_lst = list(itertools.product(*fac_one_vars_dom_lst))

    # Get a list of all factor variable domains for factor_two
    fac_two_vars_dom_lst = []
    for fac_two_vars in factor_two_scope:
        fac_two_vars_dom_lst.append(fac_two_vars.domain())

    # Get all variable domain combinations for factor_two
    fac_two_prod_lst = list(itertools.product(*fac_two_vars_dom_lst))

    # Scope for new factor with variable order preserved
    combined_scope = list(factor_one_scope)
    for fac_two_vars in factor_two_scope:
        if fac_two_vars not in combined_scope:
            combined_scope.append(fac_two_vars)

    # Create a new factor for returning
    new_factor = Factor("New Factor", combined_scope)
    new_comb_val_lst = []

    if len(common_vars_lst) == 0: # If no common variables between factors
        # Get all possible combinations of variables and get new values
        for fac_one_comb in fac_one_prod_lst:
            for fac_two_comb in fac_two_prod_lst:
                # Get factor_one and factor_two values to multiply together
                new_val = factor_one.get_value(fac_one_comb) * factor_two.get_value(fac_two_comb)

                # Combine domain values their new value
                combined_comb = list(fac_one_comb)
                combined_comb.extend(fac_two_comb)
                combined_comb.append(new_val)
                new_comb_val_lst.append(combined_comb)

    else: # If there are common variables between factors
        # Get all possible combinations of variables and get new values
        for fac_one_comb in fac_one_prod_lst:
            for fac_two_comb in fac_two_prod_lst:

                # Check for overlapping variables
                same_ele = 0
                for c_var_loc in c_var_loc_lst:
                    if fac_one_comb[c_var_loc[0]] == fac_two_comb[c_var_loc[1]]:
                        same_ele = same_ele + 1

                # If the variables overlap, get factor_one and factor_two values to multiply together
                if same_ele == len(common_vars_lst):
                    new_val = factor_one.get_value(fac_one_comb) * factor_two.get_value(fac_two_comb)
                    combined_comb = list(fac_one_comb)

                    # Combine variable domain values while preserving order
                    for i in range(len(fac_two_comb)):
                        is_repeat = False
                        for c_var_loc in c_var_loc_lst:
                            if i == c_var_loc[1]:
                                is_repeat = True
                        if is_repeat is False:
                            combined_comb.append(fac_two_comb[i])

                    # Combine domain values their new value
                    combined_comb.append(new_val)
                    new_comb_val_lst.append(combined_comb)

    # Add new values to the factor
    new_factor.add_values(new_comb_val_lst)

    return new_factor


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''

    # Setup for factor scope variables
    fac_scope = f.get_scope()
    var_pos = fac_scope.index(var)
    combined_scope = list(fac_scope)
    combined_scope.pop(var_pos)

    # Get a list of all factor variable domains
    fac_var_dom_lst = []
    for fac_var in fac_scope:
        fac_var_dom_lst.append(fac_var.domain())

    # Get all variable domain combinations
    fac_prod_lst = list(itertools.product(*fac_var_dom_lst))

    # Create a new factor for returning
    new_factor = Factor("New Factor", combined_scope)
    new_comb_val_lst = []

    # Loop over all factor combinations
    for fac_comb in fac_prod_lst:
        if fac_comb[var_pos] == value: # Factor combination has specified value

            # Get factor combination value and their corresponding value
            combined_comp = list(fac_comb)
            combined_comp.pop(var_pos)
            combined_comp.append(f.get_value(fac_comb))
            new_comb_val_lst.append(combined_comp)

    # Add new values to the factor
    new_factor.add_values(new_comb_val_lst)

    return new_factor


def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''

    # Setup for factor scope variables
    fac_scope = f.get_scope()
    var_pos = fac_scope.index(var)
    combined_scope = list(fac_scope)
    combined_scope.pop(var_pos)

    # Get a list of all factor variable domains
    fac_var_dom_lst = []
    for fac_var in fac_scope:
        fac_var_dom_lst.append(fac_var.domain())

    # Get all variable domain combinations
    fac_prod_lst = list(itertools.product(*fac_var_dom_lst))

    # List for keeping track of seen variable domain combinations
    checked_fac_prod_lst = []

    # Create a new factor for returning
    new_factor = Factor("New Factor", combined_scope)
    new_comb_val_lst = []

    # Loop over all factor combinations
    for fac_comb in fac_prod_lst:
        if fac_comb not in checked_fac_prod_lst: # Ensure combination is new
            checked_fac_prod_lst.append(fac_comb)
            fac_comb_cpy = list(fac_comb)
            fac_comb_cpy.pop(var_pos)

            # Variable for factor domain combination values sum
            acc_value = 0

            # Loop over all factor combinations again
            for other_fac_comb in fac_prod_lst:
                if other_fac_comb not in checked_fac_prod_lst: # Ensure combination is new
                    other_fac_comb_cpy = list(other_fac_comb)
                    other_fac_comb_cpy.pop(var_pos)

                    # If combination with summed out value matches, sum their combination values together
                    if fac_comb_cpy == other_fac_comb_cpy:
                        acc_value = acc_value + f.get_value(fac_comb) + f.get_value(other_fac_comb)
                        checked_fac_prod_lst.append(other_fac_comb)

            # Get factor combination value and their corresponding value
            new_value = acc_value
            combined_comp = list(fac_comb_cpy)
            combined_comp.append(new_value)
            new_comb_val_lst.append(combined_comp)

    # Add new values to the factor
    new_factor.add_values(new_comb_val_lst)

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

    bn_facs = Net.factors()
    bn_facs_cpy = list(bn_facs)

    # Loop over all evidence variables and for each evidence variable, loop over all factors and restrict ones
    # containing the current evidence variable
    for i in range(len(EvidenceVars)):
        for j in range(len(bn_facs_cpy)):
            ev_var = EvidenceVars[i]
            fac = bn_facs_cpy[j]
            fac_scope = fac.get_scope()
            if ev_var in fac_scope:
                bn_facs_cpy[j] = restrict_factor(fac, ev_var, ev_var.get_evidence())

    # Get a good variable elimination ordering
    elim_order = min_fill_ordering(bn_facs_cpy, QueryVar)
    res_bn_facs = list(bn_facs_cpy)

    # Loop over the variable elimination order and eliminate variables by multiplying and summing out
    for elim_var in elim_order:

        # Get factors that contain the current elim_var
        to_be_elim_facs_lst = []
        for fac in res_bn_facs:
            fac_scope = fac.get_scope()
            if elim_var in fac_scope:
                to_be_elim_facs_lst.append(fac)

        # Multiply the factors containing elim_var and sum out the resulting factor by elim_var
        fac_multi_prod = multiply_factors(to_be_elim_facs_lst)
        fac_sum = sum_out_variable(fac_multi_prod, elim_var)

        # Remove the eliminated factors from the list of factors
        for facs in to_be_elim_facs_lst:
            res_bn_facs.pop(res_bn_facs.index(facs))

        # Add the new factor to the list of factors
        res_bn_facs.append(fac_sum)

    # Multiply the resulting factors with each other
    result_fac = multiply_factors(res_bn_facs)
    result_fac_scope = result_fac.get_scope()

    # Get the resulting factor domain values
    result_fac_var_dom = result_fac_scope[0].domain()
    not_normalized_vals = []
    for dom_val in result_fac_var_dom:
        not_normalized_vals.append(result_fac.get_value([dom_val]))

    # Normalize the resulting factor domain values
    normalized_result_vals = normalize(not_normalized_vals)

    return normalized_result_vals
