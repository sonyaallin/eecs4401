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
from typing import List


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


def multiply_helper(scope, Factors2, new_factor):
    if len(scope) == 0:
        result = 1
        for factor in Factors2:
            result = result * factor.get_value_at_current_assignments()
        new_factor.add_value_at_current_assignment(result)
    else:
        var = scope[0]
        for val in var.domain():
            var.set_assignment(val)
            multiply_helper(scope[1:], Factors2, new_factor)


def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Fators'''
     #IMPLEMENT
    name = ''
    # scopes = [f.get_scope() for f in Factors]
    # scope = list(dict.fromkeys(scopes))
    if len(Factors) == 1:
        return Factors[0]
    scope = get_all_variables(Factors)
    new_factor = Factor(name, scope)
    multiply_helper(scope, Factors, new_factor)
    # new_factor.add_value_at_current_assignment(result)
    return new_factor

def get_all_variables(Factors):
    """
    return all unique variables.
    """
    result = []
    for factor in Factors:
        for variable in factor.get_scope():
            if variable not in result:
                result.append(variable)
    return result


def get_all_restrict_value(f, domain):
    """
    return all combinations of assignments of variables
    """
    domains = list(itertools.product(*domain))
    new_values = []
    # all combiantions of assignments of var in f
    for d in domains:
        d = list(d)
        val = f.get_value(d)
        new_values.append(d + [val])
    return new_values

def remove_value(list, scope,  var):
    """
    remove value of var in function restrict_factor since it is restricted
    """
    i = scope.index(var)
    result = []
    for sub in list:
        l = []
        for j in range(len(sub)):
            if i == j:
                pass
            else:
                l.append(sub[j])
        result.append(l)
    return result

def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    #IMPLEMENT
    name = str(f.name) + 'restricted'
    scope = f.get_scope()
    new_scope = list_without_var(scope, var)
    var.set_assignment(value)
    new_factor = Factor(name, new_scope)
    domain = []
    for v in scope:
        if v == var:
            domain.append([value])
        else:
            domain.append(v.domain())
    new_values =  get_all_restrict_value(f, domain)
    new_values = remove_value(new_values, scope, var)
    new_factor.add_values(new_values)
    return new_factor

def list_without_var(l,var):
    """
    return a new list without variable var.
    """
    new_scope = []
    for item in l:
        if item != var:
            new_scope.append(item)
    return new_scope

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    #IMPLEMENT
    name = str(f.name) + 'by sum out var'
    scope = f.get_scope()
    # i = scope.index(var)
    new_scope = list_without_var(scope, var)
    new_factor = Factor(name, new_scope)
    # if new_scope == scope: # var is not in the scope:
    # if only var in the scope
    if scope == []:
        result = []
        sum = 0
        for val in var.domain():
            sum += f.get_value([val])
        result.append([sum])
        new_factor.add_values(result)
        return new_factor
    else:
        domain = []
        for v in new_scope:
            domain.append(v.domain())
        domains = list(itertools.product(*domain))
        new_factor.add_values(get_sum_var(var, domains, f))
        return new_factor

def get_sum_var(var, domains, f):
    """
    return sum of variable var of all assignments for each domain value
    """
    scope = f.get_scope()
    i = scope.index(var)
    new_values = []
    # all assignments of var in f
    for d in domains:
        sum = 0
        for val in var.domain():
            d_list = list(d)
            d_lists = add_val(d_list, i, val)
            sum += f.get_value(d_lists)
        new_values.append(list(d) + [sum])
    return new_values

def add_val(list, i, val):
    result = []
    if len(list) == 0:
        return [val]
    if len(list)  == i:
        for item in list:
            result.append(item)
        result.append(val)
        return result
    for j in range(len(list)):
        if j != i:
            result.append(list[j])
        else:
            result.append(val)
            result.append(list[j])
    return result


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
   mean that Pr(A='a'|B=1, C='c') = 0.5 Pr(A='b'|B=1, C='c') = 0.24
   Pr(A='c'|B=1, C='c') = 0.26
    '''
    # IMPLEMENT
    # get all factors with EvidenceVars
    factors = Net.factors()
    new_factors = []
    for f in factors:
        new_factors.append(f)
    update_factors(factors, EvidenceVars, new_factors)
    Z_j = min_fill_ordering(new_factors, QueryVar)
    for z in Z_j:
        factors_with_z = []
        for f in new_factors:
            if z in f.get_scope():
                factors_with_z.append(f)
        # 2(a) of VE algorithm by slides
        g_j = sum_out_variable(multiply_factors(factors_with_z), z)
        # 2(b) which is remove f which contains z and add g_j into F
        for f_i in factors_with_z:
            new_factors.remove(f_i)
        if g_j:
            new_factors.append(g_j)
    # last step, multiply all the factor and normalize
    mf = multiply_factors(new_factors)
    result = []
    for val in QueryVar.domain():
        num = mf.get_value([val])
        result.append(num)
    answer = normalize(result)
    return answer


def update_factors(factors, EvidenceVars, new_factors):
    EvidenceVars = make_unique(EvidenceVars)
    for i in range(len(factors)):
        evidence = []
        vars_list = factors[i].get_scope()
        for evi in EvidenceVars:
            if evi in vars_list:
                evidence.append(evi)
        # replace factor with retricted factor, might be constant factor
        if evidence != []:
            for var in evidence:
                factors[i] = restrict_factor(factors[i], var, var.get_evidence())
                new_factors[i] = factors[i]

def make_unique(list):
    result = []
    for item in list:
        if not item in result:
            result.append(item)
    return result


# if __name__ == "__main__":
#     A = Variable('A', ['a', '-a'])
#     B = Variable('B', ['b', '-b'])
#     C = Variable('C', ['c', '-c'])
#     D = Variable('D', ['d', '-d'])
#     E = Variable('E', ['e', '-e'])
#     F = Variable('F', ['f', '-f'])
#     G = Variable('G', ['g', '-g'])
#     H = Variable('H', ['h', '-h'])
#     I = Variable('I', ['i', '-i'])
#     F_A = Factor('P(A)', [A])
#     F_H = Factor('P(H)', [H])
#     F_G = Factor('P(G)', [G])
#     F_F = Factor('P(F)', [F])
#     F_B = Factor('P(B|A,H)', [B, A, H])
#     F_I = Factor('P(I|B)', [I, B])
#     F_C = Factor('P(C|B,G)', [C, B, G])
#     F_E = Factor('P(E|C)', [E, C])
#     F_D = Factor('P(D|C,F)', [D, C, F])
#
#     F_A.add_values([['a', 0.9], ['-a', 0.1]])
#     F_H.add_values([['h', 0.5], ['-h', 0.5]])
#     F_G.add_values([['g', 1.0], ['-g', 0.0]])
#     F_F.add_values([['f', 0.1], ['-f', 0.9]])
#     F_I.add_values([['i', 'b', 0.3], ['-i', 'b', 0.7], ['i', '-b', 0.9], ['-i', '-b', 0.1]])
#     F_E.add_values([['e', 'c', 0.2], ['-e', 'c', 0.8], ['e', '-c', 0.4], ['-e', '-c', 0.6]])
#     F_B.add_values([['b', 'a', 'h', 1.0], ['-b', 'a', 'h', 0.0], ['b', 'a', '-h', 0.0], ['-b', 'a', '-h', 1.0],
#                    ['b', '-a', 'h', 0.5], ['-b', '-a', 'h', 0.5], ['b', '-a', '-h', 0.6], ['-b', '-a', '-h', 0.4]])
#     F_C.add_values([['c', 'b', 'g', 0.9], ['-c', 'b', 'g', 0.1], ['c', 'b', '-g', 0.9], ['-c', 'b', '-g', 0.1],
#                    ['c', '-b', 'g', 0.1], ['-c', '-b', 'g', 0.9], ['c', '-b', '-g', 1.0], ['-c', '-b', '-g', 0.0]])
#     F_D.add_values([['d', 'c', 'f', 0.0], ['-d', 'c', 'f', 1.0], ['d', 'c', '-f', 1.0], ['-d', 'c', '-f', 0.0],
#                    ['d', '-c', 'f', 0.7], ['-d', '-c', 'f', 0.3], ['d', '-c', '-f', 0.2], ['-d', '-c', '-f', 0.8]])
#
#     Q1 = BN('Q1', [A, B, C, D, E, F, G, H, I], [F_A, F_B, F_C, F_D, F_E, F_F, F_G, F_H, F_I])
#
#     A.set_evidence('a')
#     a = VE(Q1, B, [A])
#     print(a)
#
#     A.set_evidence('a')
#     b = VE(Q1, C, [A])
#     print(b)
#
#     A.set_evidence('a')
#     E.set_evidence('-e')
#     c = VE(Q1, C, [A, E])
#     print(c)
#
#     A.set_evidence('a')
#     F.set_evidence('-f')
#     d = VE(Q1, C, [A, F])
#     print(d)
