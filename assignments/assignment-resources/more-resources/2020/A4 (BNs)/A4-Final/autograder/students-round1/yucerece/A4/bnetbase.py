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

from itertools import product


class Variable:
    '''Class for defining Bayes Net variables. '''

    def __init__(self, name, domain=[]):
        '''Create a variable object, specifying its name (a
        string). Optionally specify the initial domain.
        '''
        self.name = name  # text name for variable
        self.dom = list(domain)  # Make a copy of passed domain
        self.evidence_index = 0  # evidence value (stored as index into self.dom)
        self.assignment_index = 0  # For use by factors. We can assign variables values
        # and these assigned values can be used by factors
        # to index into their tables.

    def add_domain_values(self, values):
        '''Add domain values to the domain. values should be a list.'''
        for val in values: self.dom.append(val)

    def value_index(self, value):
        '''Domain values need not be numbers, so return the index
           in the domain list of a variable value'''
        return self.dom.index(value)

    def domain_size(self):
        '''Return the size of the domain'''
        return (len(self.dom))

    def domain(self):
        '''return the variable domain'''
        return (list(self.dom))

    def set_evidence(self, val):
        '''set this variable's value when it operates as evidence'''
        self.evidence_index = self.value_index(val)

    def get_evidence(self):
        return (self.dom[self.evidence_index])

    def set_assignment(self, val):
        '''Set this variable's assignment value for factor lookups'''
        self.assignment_index = self.value_index(val)

    def get_assignment(self):
        return (self.dom[self.assignment_index])

    ##These routines are special low-level routines used directly by the
    ##factor objects
    def set_assignment_index(self, index):
        '''This routine is used by the factor objects'''
        self.assignment_index = index

    def get_assignment_index(self):
        '''This routine is used by the factor objects'''
        return (self.assignment_index)

    def __repr__(self):
        '''string to return when evaluating the object'''
        return ("{}".format(self.name))

    def __str__(self):
        '''more elaborate string for printing'''
        return ("{}, Dom = {}".format(self.name, self.dom))


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
        self.values = [0] * size  # initialize values to be long list of zeros.

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
        saved_values = []  # save and then restore the variable assigned values.
        for v in self.scope:
            saved_values.append(v.get_assignment_index())

        self.recursive_print_values(self.scope)

        for v in self.scope:
            v.set_assignment_index(saved_values[0])
            saved_values = saved_values[1:]

    def recursive_print_values(self, vars):
        if len(vars) == 0:
            print("[", end=""),
            for v in self.scope:
                print("{} = {},".format(v.name, v.get_assignment()), end="")
            print("] = {}".format(self.get_value_at_current_assignments()))
        else:
            for val in vars[0].domain():
                vars[0].set_assignment(val)
                self.recursive_print_values(vars[1:])

    def __repr__(self):
        return ("{}".format(self.name))


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
                    print(" does not appear in list of variables {}.".format(list(map(lambda x: x.name, f.get_scope())),
                                                                             v.name, list(map(lambda x: x.name, Vars))))

    def factors(self):
        return list(self.Factors)

    def variables(self):
        return list(self.Variables)


def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Factors'''
    # This function takes as input a list of Factor objects; it creates
    # and returns a new factor that is equal to the product of the factors in the list. Do not modify any of
    # the input factors. recursion inspired by recursive_print_values and print_table
    # IMPLEMENT
    num = len(Factors)
    factors = Factors[:]  # just in case

    if num is 1:  # base case
        return factors[0]
    else:
        factor1 = factors[0]
        factor2 = factors[1]
        if num is 2:
            new_name = "{} * {}".format(factor1.name, factor2.name)
            var_list = factor1.get_scope()
            # print(var_list)
            for var in factor2.get_scope():
                if var not in factor1.get_scope():
                    var_list.append(var)
            # print(var_list)
            f = Factor(new_name, var_list)
            new_vals = []
            recursive_multiply_factors(factor1, factor2, var_list, new_vals)
            # print(new_name)
            # print(new_vals)
            f.values = new_vals
            return f
        else:  # recursive call
            f = []
            new_name = "{} * {}".format(factor1.name, factor2.name)
            var_list = factor1.get_scope()
            # print(var_list)
            for var in factor2.get_scope():
                if var not in factor1.get_scope():
                    var_list.append(var)
            # print(var_list)
            factor = Factor(new_name, var_list)
            new_vals = []
            recursive_multiply_factors(factor1, factor2, var_list, new_vals)
            factor.values = new_vals
            # print(new_name)
            # print(new_vals)
            f.append(factor)
            # print(factors[1:])
            # print(factors[2:])
            f = f + factors[2:]
            # print(f)
            return multiply_factors(f)


def recursive_multiply_factors(factor1, factor2, var_list, new_vals):
    # print(var_list)
    if len(var_list) == 0:  # base case
        new_vals.append(factor1.get_value_at_current_assignments() * factor2.get_value_at_current_assignments())
    else:  # recursive call
        # print(var_list)
        for v in var_list[0].domain():
            var_list[0].set_assignment(v)
            # print(var_list[0])
            recursive_multiply_factors(factor1, factor2, var_list[1:], new_vals)

    # alternate multiple_factors, don't know how to fix it
    # var_list = list(map(Factor.get_scope, Factors))
    # print(var_list)
    # new_name_list = []
    # num = len(Factors)
    # for factor in Factors:
    #     new_name_list.append(factor.name)
    #     new_name_list.append("*")
    # #print(new_name_list)
    # new_name_list.pop(-1)
    # new_name = ''.join(new_name_list)
    # var_domains = [(map(lambda x: [(map(Variable.domain, x)), var_list)])]
    # print(var_domains)
    # mult = product(*(product(*f) for f in var_domains))
    # #print(mult)
    # new_values = []
    # for value in mult:
    #     #print(value)
    #     new_value = 1
    #     for int in range(num):
    #         new_value = new_value * Factors[int].get_value(list(value[int]))
    #     values = sum(([v] for v in value), [])
    #     new_values.append(values + [new_value])
    # print(new_values)
    # new_factor = Factor(new_name, sum(var_list, []))
    # new_factor.add_values(new_values)
    # return new_factor


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    # We can restrict factor f to X = a by setting X to the value
    # x  and “deleting” incompatible elements of f’s domain (slides)
    # IMPLEMENT
    var_list = f.get_scope()
    var_index = var_list.index(var)  # store var's index before contuning
    # print(var_index)
    # i = 0
    # index = 0
    # for v in var_list:
    #     if v is var:
    #         index = i
    #         break
    #     i += 1

    #  restrict_factor should eliminate the variable from the new factor's scope. piazza @355
    new_scope = []
    for variable in var_list:
        if variable is not var:
            new_scope.append(variable)
    domain = list((map(Variable.domain, var_list)))
    # print(domain)
    domain[var_index] = [value]
    new_factor = Factor("{} - Restricted: {} = {}".format(f.name, var, value), new_scope)

    # assign values
    all_values = product(*domain)
    # print(*all_values)
    updated_values = []
    for v in all_values:
        # print(v)
        vals = f.get_value(list(v))
        # curr = list(v).pop(var_index)
        # print(curr)
        curr = list(v)
        # print(curr)
        curr.pop(var_index)
        # print(curr)
        updated_values.append(curr + [vals])
    # print(updated_values)
    new_factor.add_values(updated_values)
    return new_factor


def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    # This function takes as input a single factor, and a variable V;
    # it creates and returns a new factor that is the result of summing V out of the input factor. Do not
    # modify the input factor.
    # IMPLEMENT
    var_list = f.get_scope()
    var_index = var_list.index(var)  # store var's index before contuning
    new_scope = []
    for variable in var_list:
        if variable is not var:
            new_scope.append(variable)
    domain = list((map(Variable.domain, new_scope)))
    new_factor = Factor("{} - Summed out: {}".format(f.name, var), new_scope)

    # assign values and add the summed out var
    all_values = product(*domain)
    # print(*all_values)
    updated_values = []
    for v in all_values:
        temp = 0
        for val in var.domain():
            curr = list(v)
            curr.insert(var_index, val)
            # print(curr)
            temp += f.get_value(curr)
        updated_values.append(list(v) + [temp])
    # print(updated_values)
    new_factor.add_values(updated_values)
    return new_factor


def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''
    s = sum(nums)
    if s == 0:
        newnums = [0] * len(nums)
    else:
        newnums = []
        for n in nums:
            newnums.append(n / s)
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
        (var, new_scope) = min_fill_var(scopes, Vars)
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
    (minfill, min_new_scope) = compute_fill(scopes, Vars[0])
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
    # IMPLEMENT
    # Using the Variable Elimination Algorithm Steps from Lecture Slides
    factors = Net.factors()[:]

    # Step 1: Replace each factor f∈F that mentions a variable(s) in E
    # with its restriction f_{E=e} (this might yield a “constant” factor)
    for i in range(len(factors)):
        for v in EvidenceVars:
            if v in factors[i].get_scope():
                temp = restrict_factor(factors[i], v, v.get_evidence())
                factors[i] = temp

    # Step 2: For each Z_j - in the order given - eliminate Z_j ∈ Z as follows:
    # (a) Compute new factor g_j = ∑_{Z_j} f_1 x f_2 x ... x f_k where f_i are
    # the factors in F that include Z_j
    # (b) Remove the factors f_i (that mention Z) from F and add new factor g_j to F
    min_fill_ord = min_fill_ordering(factors, QueryVar)
    for v in min_fill_ord:
        temp_mult = []
        for f in factors:
            if v in f.get_scope():
                temp_mult.append(f)
        for factor in temp_mult:
            factors.remove(factor)
        updated_factor = sum_out_variable(multiply_factors(temp_mult), v)
        factors.append(updated_factor)

    # Step 3: The remaining factors at the end of this process will refer only to the
    # query variable Q. Take their product and normalize to produce P(Q|E).
    mult = multiply_factors(factors)
    distribution = []
    for val in QueryVar.domain():
        distribution.append(mult.get_value([val]))
    if sum(distribution) is 0:
        normalized_dist = [float("inf")] * len(distribution)
    else:
        normalized_dist = [v / sum(distribution) for v in distribution]
    return normalized_dist


#if __name__ == '__main__':
    #     # Part 2, Question 1
    #     a = Variable('a', ['a', '-a'])
    #     b = Variable('b', ['b', '-b'])
    #     c = Variable('c', ['c', '-c'])
    #     d = Variable('d', ['d', '-d'])
    #     e = Variable('e', ['e', '-e'])
    #     f = Variable('f', ['f', '-f'])
    #     g = Variable('g', ['g', '-g'])
    #     h = Variable('h', ['h', '-h'])
    #     i = Variable('i', ['i', '-i'])
    #
    #     FA = Factor('P(a)', [a])
    #     FB = Factor('P(b|ah)', [b, a, h])
    #     FC = Factor('P(c|bg)', [c, b, g])
    #     FD = Factor('P(d|cf)', [d, c, f])
    #     FE = Factor('P(e|c)', [e, c])
    #     FF = Factor('P(f)', [f])
    #     FG = Factor('P(g)', [g])
    #     FH = Factor('P(h)', [h])
    #     FI = Factor('P(i|b)', [i, b])
    #
    #     FA.add_values([['a', 0.9], ['-a', 0.1]])
    #     FB.add_values([['b', 'a', 'h', 1.0], ['b', 'a', '-h', 0.0],
    #                    ['b', '-a', 'h', 0.5], ['-b', 'a', 'h', 0.0],
    #                    ['b', '-a', '-h', 0.6], ['-b', 'a', '-h', 1.0],
    #                    ['-b', '-a', 'h', 0.5], ['-b', '-a', '-h', 0.4]])
    #     FC.add_values([['c', 'b', 'g', 0.9], ['c', 'b', '-g', 0.9],
    #                    ['c', '-b', 'g', 0.1], ['-c', 'b', 'g', 0.1],
    #                    ['c', '-b', '-g', 1.0], ['-c', 'b', '-g', 0.1],
    #                    ['-c', '-b', 'g', 0.9], ['-c', '-b', '-g', 0.0]])
    #     FD.add_values([['d', 'c', 'f', 0.0], ['d', 'c', '-f', 1.0],
    #                    ['d', '-c', 'f', 0.7], ['-d', 'c', 'f', 1.0],
    #                    ['d', '-c', '-f', 0.2], ['-d', 'c', '-f', 0.0],
    #                    ['-d', '-c', 'f', 0.3], ['-d', '-c', '-f', 0.8]])
    #     FE.add_values([['e', 'c', 0.2], ['e', '-c', 0.4], ['-e', 'c', 0.8],
    #                    ['-e', '-c', 0.6]])
    #     FF.add_values([['f', 0.1], ['-f', 0.9]])
    #     FG.add_values([['g', 1.0], ['-g', 0.0]])
    #     FH.add_values([['h', 0.5], ['-h', 0.5]])
    #     FI.add_values([['i', 'b', 0.3], ['i', '-b', 0.9], ['-i', 'b', 0.7],
    #                    ['-i', '-b', 0.1]])
    #
    #     Q1 = BN('Q1', [a, b, c, d, e, f, g, h, i], [FA, FB, FC, FD, FE, FF, FG, FH, FI])
    #     # (a)
    #     a.set_evidence('a')
    #     ba = VE(Q1, b, [a])
    #
    #     # (b)
    #     a.set_evidence('a')
    #     ca = VE(Q1, c, [a])
    #
    #     # (c)
    #     a.set_evidence('a')
    #     e.set_evidence('-e')
    #     cae = VE(Q1, c, [a, e])
    #
    #     # (d)
    #     a.set_evidence('a')
    #     f.set_evidence('-f')
    #     caf = VE(Q1, c, [a, f])
    #
    #     # answers
    #     print("a={}; b={}; c={}; d={}".format(ba[0], ca[0], cae[0], caf[0]))
    #     # a=0.5; b=0.5; c=0.5714285714285714; d=0.5

    # Part 2, Question 2
    # (a)  Show a case of conditional independence in the Net where knowing some
    # evidence item V1 = d1 makes another evidence item V2 = d2 irrelevant to the probability of
    # some third variable V3. (Note that conditional independence requires that the independence
    # holds for all values of V3).
    # Answer: Given knowledge about Battery Voltage (V1), knowing about Voltage at Plug (V2) won't tell
    # anything more about Headlights (V3)

    # (b) Show a case of conditional independence in the Net where two variables are
    # independent given NO evidence at a third variable yet dependent given evidence at the third
    # variable.
    # Asking essentially for V1, V2, V3 such that P(V1|V2) = P(V1) and P(V2|V1) = P(V2)
    # but P(V1|V2,V3) != P(V1|V3) @piazza 405
    # Answer: Voltage at Plug (V1) and Spark Plugs (V2) are independent given no evidence at Spark Quality (V3)
    # yet dependent given evidence at Spark Quality (V3).
    # Demo code I used on carDiagnosis.py to demonstrate
    # pv.set_evidence('strong')
    # b = VE(car, sp, [pv])
    # print(b[0])
    # sp.set_evidence('okay')
    # bb = VE(car, pv, [sp])
    # print(bb[0])
    # sp.set_evidence('okay')
    # sq.set_evidence('bad')
    # bbb = VE(car, pv, [sp, sq])
    # print(bbb[0])
    # sq.set_evidence('bad')
    # bbbb = VE(car, pv, [sq])
    # print(bbbb[0])

    # (c) Show a sequence of accumulated evidence items V1 = d1,...,V k = dk (i.e.,
    # each evidence item in the sequence is added to the previous evidence items) such that each
    # additional evidence item increases the probability that some variable V has the value d.
    # (That is, the probability of V = d increases monotonically as we add evidence items).
    # What is P(V = d—V1 = d1,...,Vk = dk)?
    # Answer:
    # Battery Age - ba (new) (V1), Battery Voltage - bv (strong) (V2), Spark Quality - sq (good) (V3),
    # Start System - ss (okay) (V4), Car Cranks - cc(true) (V5),
    # Car Starts st ? (V0)
    # ba.set_evidence('new')
    # ev01 = VE(car, st, [ba])
    # print(ev01[0])
    # ba.set_evidence('new')
    # bv.set_evidence('strong')
    # ev012 = VE(car, st, [ba, bv])
    # print(ev012[0])
    # ba.set_evidence('new')
    # bv.set_evidence('strong')
    # sq.set_evidence('good')
    # ev0123 = VE(car, st, [ba, bv, sq])
    # print(ev0123[0])
    # ba.set_evidence('new')
    # bv.set_evidence('strong')
    # sq.set_evidence('good')
    # ss.set_evidence('okay')
    # ev01234 = VE(car, st, [ba, bv, sq, ss])
    # print(ev01234[0])
    # ba.set_evidence('new')
    # bv.set_evidence('strong')
    # sq.set_evidence('good')
    # ss.set_evidence('okay')
    # cc.set_evidence('true')
    # ev012345 = VE(car, st, [ba, bv, sq, ss, cc])
    # print(ev012345[0])
    # progression: 0.31555106857312093
    #              0.5631201041803289
    #              0.6785611409462576
    #              0.694713220205456
    #              0.8683915252568202

    # (d) Show a sequence of accumulated evidence items V1 = d1,...,V k = dk (i.e.,
    # each evidence item in the sequence is added to the previous evidence items) such that each
    # additional evidence item decreases the probability that some variable V has the value d.
    # (That is, the probability of V = d decreases monotonically as we add evidence items). What
    # is P(V = d—V1 = d1,...,Vk = dk)?
    # Answer:
    # Battery Age - ba (new) (V1), Battery Voltage - bv (weak) (V2), Start System - ss (faulty) (V3),
    # Spark Plugs - sp (too wide) (V4), Car Cranks - cc(false) (V5)
    # Car Starts st (true) (V0)
    # ba.set_evidence('new')
    # ev01 = VE(car, st, [ba])
    # print(ev01[0])
    # ba.set_evidence('new')
    # bv.set_evidence('weak')
    # ev012 = VE(car, st, [ba, bv])
    # print(ev012[0])
    # ba.set_evidence('new')
    # bv.set_evidence('weak')
    # ss.set_evidence('faulty')
    # ev0123 = VE(car, st, [ba, bv, ss])
    # print(ev0123[0])
    # ba.set_evidence('new')
    # bv.set_evidence('weak')
    # sp.set_evidence('too_wide')
    # ss.set_evidence('faulty')
    # ev01234 = VE(car, st, [ba, bv, sp, ss])
    # print(ev01234[0])
    # ba.set_evidence('new')
    # bv.set_evidence('weak')
    # sp.set_evidence('too_wide')
    # ss.set_evidence('faulty')
    # cc.set_evidence('false')
    # ev012345 = VE(car, st, [ba, bv, ss, sp, cc])
    # print(ev012345[0])
    # progression = 0.31555106857312093
    #               0.2735619894239697
    #               0.01745685249285633
    #               0.0
    #               0.0
