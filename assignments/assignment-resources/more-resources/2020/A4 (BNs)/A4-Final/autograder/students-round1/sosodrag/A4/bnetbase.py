import itertools

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


def get_disjoint_vars(F):
    '''
    Build a dictionary of all common vars in Factors (F)
    :param F: All factors
    :return: vars not common among all factors (ie disjoint set)
    '''

    disjoint_set = {}
    intersection_set = {}

    for f in F:
        for v in f.get_scope():
            if v.name not in disjoint_set:
                disjoint_set[v.name] = v
            else:
                #print("Duplicate found: {}".format(v.name))
                intersection_set[v.name] = disjoint_set.pop(v.name)

    #print("Inter set: {}".format(intersection_set))
    return intersection_set, disjoint_set


def get_F_scopes(F, ex_vars=False):
    """
    Package all variables linked to each factor in F in a list. Optionally exclude those 'common' variables in ex_vars.

    :param F: List containing factors
    :param ex_vars: A dict of all intersecting vars ie: all common vars amongst in factors of F
    :return: A single 1 level list of all scoped variables of factors in F
    """
    scopes = []

    for f in F:
        current_scope = f.get_scope()
        #print("get_F_scopes: scopes = {}, current_scope = {}".format(scopes, current_scope))
        if ex_vars:
            for v in f.get_scope():
                if v in scopes:
                    #print("get_F_scopes: scopes: {}, already in scope = {}".format(scopes, v))
                    current_scope.remove(v)

        scopes += current_scope

    return scopes


def get_F_scope_vals(scopes, restrict_tuple=()):
    """
    Based on passed in list of scopes, collect all the domain values for each var in scopes
    :param scopes: list containing vars
    :return: All var domains in scopes
    """
    values = []

    for v in scopes:

        if len(restrict_tuple) > 0 and v == restrict_tuple[0]: # If we're looking at the var whose values need to be restricted
            #print("restricting val {} on var: {}".format(restrict_tuple[1], restrict_tuple[0]))
            custom_dom = [d for d in v.domain() if d == restrict_tuple[1]]
            values.append(custom_dom)
        else:
            values.append(v.domain())

    #print("values: {}".format(values))
    return values

def gen_F_table_rows(cp, set, F_scopes, restrict_val_exclude):
    """
    Generate the table rows for a new factor product
    :param cp: Cross product calculated in parent call
    :return: a list containing "rows" for new factor product
    """

    table_rows = []

    for p in cp:
        var_val = list(zip(F_scopes, p))
        #print("Zipped: {}".format(list(var_val)))

        row = []

        #print("len of var_val list: {}".format(len(list(var_val))))

        for var, val in var_val:
            var.set_assignment(val)
            row.append(val)
            #print("row after appending val: {}".format(row))

        mult = 1

        for f in set:
            mult = mult * f.get_value_at_current_assignments()

        #if restrict_val_exclude is not None:
        #    row.pop(row.index(restrict_val_exclude))

        row.append(mult)
        #print("row: {}".format(row))
        table_rows.append(row)

    #print("table_rows = {}".format(table_rows))
    return table_rows


def prod(F, exclude_vars={}, restrict_tuple=(), restrict_val_exclude=None):
    """
    Construct a table of variable assignments and respective values to use in new Factor obj.

    :param F: List of f factors
    :param exclude_vars: Obj containing 'overlapping/intersecting' vars that could potentially be excluded
    :param restrict_tuple: A (var, value) tuple sent as part of restrict_var() call
    :param restrict_val_exclude: Whether to exclude the restricted val ....
    :return: New factor object
    """
    F_scopes = get_F_scopes(F, True if len(exclude_vars) > 0 else False)
    #print("PROD: F_scopes= {}".format(list(F_scopes)))
    values_list = get_F_scope_vals(F_scopes, restrict_tuple)
    prods = [list(p) for p in itertools.product(*values_list)]

    #print("prods: {}".format(prods))

    if len(restrict_tuple) > 0:
        # Find location of restricting var name in F name
        var_index = F[0].name.find(restrict_tuple[0].name)
        factor_name = F[0].name[0: var_index + 1] + '={}'.format(restrict_tuple[1]) + F[0].name[var_index + 1:]
    else:
        cond_vars = ','.join([v.name for v in F_scopes[1:]])
        factor_name = "P({})".format(F_scopes[0].name) if not cond_vars else "P({}|{})".format(F_scopes[0].name, cond_vars)

    factor_table_rows = gen_F_table_rows(prods, F, F_scopes, restrict_val_exclude)

    new_factor = Factor(factor_name, F_scopes)
    new_factor.add_values(factor_table_rows)

    #print("factor_name: {}".format(factor_name))
    #print("factor_table_rows: {}".format(factor_table_rows))
    return new_factor


def gen_summed_rows(F, summed_var, summed_var_domain_val):
    """
    Generate the "summed out var" table.

    :param f: Factor whose row values will be summed
    :return: list which is a "summed out" row over some var passed into calling function
    """

    F_scopes = get_F_scopes(F, True)
    values_list = get_F_scope_vals(F_scopes)
    prods = [list(p) for p in itertools.product(*values_list)]

    #print("summed_rows prod: {}".format(prods))


def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Fators'''

    if len(Factors) == 1:
        return Factors[0]
    else:
        inter_set, dis_set = get_disjoint_vars(Factors)
        if not len(inter_set):
            return prod(Factors)
        return prod(Factors, inter_set)


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''

    return prod([f], restrict_tuple=(var, value), restrict_val_exclude=True)


def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''

    F_scopes = get_F_scopes([f], True)
    values_list = get_F_scope_vals(F_scopes)
    prods = [list(p) for p in itertools.product(*values_list)]

    var_index_in_F_scope = F_scopes.index(var)
    #print("var_index_in_F_scope = {}".format(var_index_in_F_scope))

    #print("var to sum out: {}".format(var))
    #print("prods prior to adding % value: {}".format(prods))

    for p in prods:
        p.append(f.get_value(p))

    #print("prods: {}".format(prods))

    for p in prods:
        #print("Targetting row: {}, var: {}, var domain: {}".format(p, var.name, var.domain()))
        # Create copy of p row, since we will alter p by popping off d if d is in p
        p_copy = list(p)
        for d in var.domain():
            if d == p_copy[var_index_in_F_scope]:
                p.pop(var_index_in_F_scope)
                #print("Sum out {} - popping: {}, index: {}".format(var.name, p.pop(var_index_in_F_scope), var_index_in_F_scope))

        if len(p) < 1:
            print("len(p) == {}, Removing: {}".format(len(p), p))
            prods.remove(p)

    #print("SUM OUT prods: {}".format(prods))

    # If the below is true, then we're dealing with a constant factor
    if all(len(p) == 1 for p in prods):
        #print("Encountered constant factor, all(len(p) == 1)")
        s = sum(sum(prods, []))
        f = Factor("name", [])
        f.add_value_at_current_assignment(s)
        return f

    table_rows = []
    seen_values = []

    for p in prods:

        if p[:-1] not in seen_values:
            #print("p[:-1] = {}".format(p[:-1]))
            matching_rows = [s for s in prods if s is not p and p[:-1] == s[:-1]]
            matching_rows.append(p)
            #print("matching rows: {}".format(matching_rows))
            s = sum(r[-1] for r in matching_rows)
            #print("s is: {}".format(s))

            p[-1] = s
            seen_values.append(p[:-1])
            table_rows.append(p)

    #print("sum_out_variable: SUM OUT prods: {}".format(table_rows))
    new_scopes = []
    for s in F_scopes:
        # print("s = {}, var = {}".format(s, var))
        # print("var == s: {}".format(var == s))
        if var is not s:
            #print("Appending: {}, {}".format(var, s))
            new_scopes.append(s)

    #print("new_scopes = {}".format(new_scopes))
    f = Factor("name", new_scopes)
    f.add_values(table_rows)
    #print("f factor = {}".format(f.print_table()))
    return f


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

    current_factors = Net.factors()

    # All those factors that had an evidence_var in their scope and were therefore removed
    # from current_factors
    removed_factors = []

    # min_fill_vars = min_fill_ordering(current_factors, QueryVar)

    for evidence_var in EvidenceVars:
        evidence = evidence_var.get_evidence()
        #print("EVIDENCE IS: {}".format(evidence))
        if evidence:
            for f in Net.factors():
                if evidence_var in f.get_scope() and f not in removed_factors:
                    f_index = current_factors.index(f)
                    r_factor = restrict_factor(f, evidence_var, evidence)
                    removed_factors.append(current_factors.pop(f_index))
                    current_factors.insert(f_index, r_factor)
        else:
            print("Error: No evidence given for: {}".format(evidence_var))

    # min_fill does not contain QueryVar, but should also not contain Z vars?
    min_fill_vars = min_fill_ordering(current_factors, QueryVar)

    for var in min_fill_vars:

        f_containing_var = []

        for f in current_factors:
            if var in f.get_scope():
                f_containing_var.append(f)

        f = multiply_factors(f_containing_var)
        #print("Multiplied factors:")
        #print(f.print_table())
        sum_f = sum_out_variable(f, var)
        #print()
        for f in f_containing_var:
            current_factors.remove(f)

        current_factors.append(sum_f)

    final_prod = multiply_factors(current_factors)

    F_scopes = get_F_scopes([final_prod], ex_vars=True)
    values_list = get_F_scope_vals(F_scopes)
    prods = [list(p) for p in itertools.product(*values_list)]

    values = []

    for p in prods:
        values.append(final_prod.get_value(p))

    norm_vals = normalize(values)
    #print("norm_vals: {}".format(norm_vals))

    return normalize(norm_vals)
