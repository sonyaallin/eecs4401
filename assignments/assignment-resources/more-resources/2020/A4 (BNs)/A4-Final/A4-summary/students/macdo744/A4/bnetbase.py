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

def multiply_factors(factors):
    '''return a new factor that is the product of the factors in Fators'''
    # format of new var is [X, Y, Z], where all of X and Z are in OG order, and Y in order of left array
    left_factor = factors[0]
    for i in range(1, len(factors)):
        left_factor = multiply_two(left_factor, factors[i])
    return left_factor


def multiply_two(factor1, factor2):
    new_scope = factor1.get_scope()
    new_scope += [x for x in factor2.get_scope() if x not in new_scope]
    product = Factor(factor1.name + '*' + factor2.name, new_scope)

    common_vars = [x for x in factor1.get_scope() if x in factor2.get_scope()]

    common = generate_assignments(common_vars, [], True)

    for assignment in common:
        for i in range(0, len(common_vars)):
            common_vars[i].set_assignment(assignment[i])
        left = generate_assignments(factor1.get_scope(), common_vars, False)
        right = generate_assignments(factor2.get_scope(), common_vars, False)
        for a1 in left:
            for a2 in right:
                common_ind = [factor2.scope.index(var) for var in common_vars]
                value = a1 + [a2[i] for i in range(0, len(a2)) if i not in common_ind]
                value += [factor1.get_value(a1) * factor2.get_value(a2)]
                product.add_values([value])
    return product

def generate_assignments(scope, restrictions, evidence):
    assignments = [[]]
    for v in scope:
        new_assignments = list()
        while len(assignments) > 0:
            old_tuple = assignments.pop(0)
            if restrictions != [] and v in restrictions:
                temp = old_tuple[:]
                if evidence:
                    temp.append(restrictions[restrictions.index(v)].get_evidence())
                else:
                    temp.append(restrictions[restrictions.index(v)].get_assignment())
                new_assignments.append(temp)
            else:
                for val in v.domain():
                    temp = old_tuple[:]
                    temp.append(val)
                    new_assignments.append(temp)
        assignments = new_assignments
    return assignments


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    scope = f.get_scope()
    for v in scope:
        if var.name == v.name:
            v.set_assignment(value)
            scope.remove(v)
    new_factor = Factor(f.name + " rest " + var.name, scope)
    new_values = restrict_helper(f, f.get_scope(), var, value, [])
    new_factor.add_values(new_values)
    return new_factor

def restrict_helper(f, vars, var, evidence, all_values):
    # base case: combination have been generated
    if vars == []:
        index = -1
        f_scope = f.get_scope()
        for i in range(len(f_scope)):
            if f_scope[i].name == var.name:
                index = i

        # use only the value for the evidence value
        if all_values == []:
            all_values = [[f.get_value([evidence])]]
        else:
            for value in all_values:
                temp = list(value)
                temp.insert(index, evidence)
                value.append(f.get_value(temp))

        return all_values

    else:
        # make all combinations of variables up until this point
        if vars[0].name != var.name:
            new_values = []
            if all_values == []:
                for val in vars[0].domain():
                    new_values.append([val])
            else:
                for array in all_values:
                    for val in vars[0].domain():
                        temp = list(array)
                        temp.append(val)
                        new_values.append(temp)
            all_values = new_values
        return restrict_helper(f, vars[1:], var, evidence, all_values)

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    new_values = sum_over(f, f.get_scope(), var, [])
    new_scope = []
    for v in f.get_scope():
        if v.name != var.name:
            new_scope.append(v)
    name = f.name + " - " + var.name
    new_factor = Factor(name, new_scope)
    new_factor.add_values(new_values)
    return new_factor

def sum_over(f, vars, var, all_values):
    # base case: combination have been generated
    if vars == []:
        index = -1
        f_scope = f.get_scope()
        for i in range(len(f_scope)):
            if f_scope[i].name == var.name:
                index = i

        # sum over all values of var to find new values
        if all_values == []:
            total = 0
            for out_val in var.domain():
                total += f.get_value([out_val])
            all_values = [[total]]
        else:
            for value in all_values:
                total_sum = 0
                for out_val in var.domain():
                    temp = list(value)
                    temp.insert(index, out_val)
                    total_sum += f.get_value(temp)
                value.append(total_sum)

        return all_values

    else:
        # make all combinations of variables up until this point
        if vars[0].name != var.name:
            new_values = []
            if all_values == []:
                for val in vars[0].domain():
                    new_values.append([val])
            else:
                for array in all_values:
                    for val in vars[0].domain():
                        temp = list(array)
                        temp.append(val)
                        new_values.append(temp)
            all_values = new_values
        return sum_over(f, vars[1:], var, all_values)


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


# find the same variable in the factor's scope
def is_var_in_factor(factor, var):
    for v in factor.get_scope():
        if var.name == v.name:
            return v
    return None

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
    factors = Net.factors()
    new_list = []

    #restrict factors
    for factor in factors:
        temp = factor
        for evidence in EvidenceVars:
            var = is_var_in_factor(factor, evidence)
            if var:
                temp = restrict_factor(temp, var, var.domain()[evidence.evidence_index])
        new_list.append(temp)

    factors = new_list
    ordering = min_fill_ordering(factors, QueryVar)

    #multiply and sum out factors until none are left
    while ordering != []:
        curr_var = ordering.pop(0)
        curr_factors = []

        #get all factors that use this variable
        for factor in factors:
            if is_var_in_factor(factor, curr_var):
                curr_factors.append(factor)

        for factor in curr_factors:
                factors.remove(factor)

        #multiply all factors that depend on current var
        multiplied_factor = None
        if len(curr_factors) > 1:
            multiplied_factor = multiply_factors(curr_factors)
        else:
            multiplied_factor = curr_factors[0]

        #sum out current variable
        summed_factor = sum_out_variable(multiplied_factor, curr_var)
        factors.append(summed_factor)

    #multiply remaining factors
    final_values = []
    for val in QueryVar.domain():
        for factor in factors:
            f_var = is_var_in_factor(factor, QueryVar)
            if f_var:
                f_var.set_assignment(val)
        product = 1
        for f in factors:
            product = product * f.get_value_at_current_assignments()
        final_values.append(product)

    return normalize(final_values)
