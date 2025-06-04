from typing import List, Set
from itertools import product

"""Classes for variable elimination Routines 
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

    """


class Variable:
    """Class for defining Bayes Net variables. """

    def __init__(self, name, domain=[]):
        """Create a variable object, specifying its name (a
        string). Optionally specify the initial domain.
        """
        self.name = name  # text name for variable
        self.dom = list(domain)  # Make a copy of passed domain
        self.evidence_index = 0  # evidence value (stored as index into self.dom)
        self.assignment_index = 0  # For use by factors. We can assign variables values
        # and these assigned values can be used by factors
        # to index into their tables.

    def add_domain_values(self, values):
        """Add domain values to the domain. values should be a list."""
        for val in values:
            self.dom.append(val)

    def value_index(self, value):
        """Domain values need not be numbers, so return the index
           in the domain list of a variable value"""
        return self.dom.index(value)

    def domain_size(self):
        """Return the size of the domain"""
        return len(self.dom)

    def domain(self):
        """return the variable domain"""
        return list(self.dom)

    def set_evidence(self, val):
        """set this variable's value when it operates as evidence"""
        self.evidence_index = self.value_index(val)

    def get_evidence(self):
        return self.dom[self.evidence_index]

    def set_assignment(self, val):
        """Set this variable's assignment value for factor lookups"""
        self.assignment_index = self.value_index(val)

    def get_assignment(self):
        return self.dom[self.assignment_index]

    ##These routines are special low-level routines used directly by the
    ##factor objects
    def set_assignment_index(self, index):
        """This routine is used by the factor objects"""
        self.assignment_index = index

    def get_assignment_index(self):
        """This routine is used by the factor objects"""
        return self.assignment_index

    def __repr__(self):
        """string to return when evaluating the object"""
        return "{}".format(self.name)

    def __str__(self):
        """more elaborate string for printing"""
        return "{}, Dom = {}".format(self.name, self.dom)


class Factor:

    """Class for defining factors. A factor is a function that is over
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
    factor is restricted."""

    def __init__(self, name, scope):
        """create a Factor object, specify the Factor name (a string)
        and its scope (an ORDERED list of variable objects)."""
        self.scope = list(scope)
        self.name = name
        size = 1
        for v in scope:
            size = size * v.domain_size()
        self.values = [0] * size  # initialize values to be long list of zeros.

    def get_scope(self):
        """returns copy of scope...you can modify this copy without affecting 
           the factor object"""
        return list(self.scope)

    def add_values(self, values):
        """This routine can be used to initialize the factor. We pass
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
         (A=2,B=b,C='light) is 2.25"""

        for t in values:
            index = 0
            for v in self.scope:
                index = index * v.domain_size() + v.value_index(t[0])
                t = t[1:]
            self.values[index] = t[0]

    def add_value_at_current_assignment(self, number):

        """This function allows adding values to the factor in a way
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
        """

        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        self.values[index] = number

    def get_value(self, variable_values):

        """This function is used to retrieve a value from the
        factor. We pass it an ordered list of values, one for every
        variable in self.scope. It then returns the factor's value on
        that set of assignments.  For example, if self.scope = [A, B,
        C], and A.domain() = [1,2,3], B.domain() = ['a', 'b'], and
        C.domain() = ['heavy', 'light'], and we invoke this function
        on the list [1, 'b', 'heavy'] we would get a return value
        equal to the value of this factor on the assignment (A=1,
        B='b', C='light')"""

        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.value_index(variable_values[0])
            variable_values = variable_values[1:]
        return self.values[index]

    def get_value_at_current_assignments(self):

        """This function is used to retrieve a value from the
        factor. The value retrieved is the value of the factor when
        evaluated at the current assignment to the variables in its
        scope.

        For example, if self.scope = [A, B, C], and A.domain() =
        [1,2,3], B.domain() = ['a', 'b'], and C.domain() = ['heavy',
        'light'], and we had previously invoked A.set_assignment(1),
        B.set_assignment('a') and C.set_assignment('heavy'), then this
        function would return the value of the factor on the
        assigments (A=1, B='1', C='heavy')"""

        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        return self.values[index]

    def print_table(self):
        """print the factor's table"""
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
            print("] = {:.3f}".format(self.get_value_at_current_assignments()))
        else:
            for val in vars[0].domain():
                vars[0].set_assignment(val)
                self.recursive_print_values(vars[1:])

    def __repr__(self):
        return "{}".format(self.name)


class BN:

    """Class for defining a Bayes Net.
       This class is simple, it just is a wrapper for a list of factors. And it also
       keeps track of all variables in the scopes of these factors"""

    def __init__(self, name, Vars, Factors):
        self.name = name
        self.Variables = list(Vars)
        self.Factors = list(Factors)
        for f in self.Factors:
            for v in f.get_scope():
                if not v in self.Variables:
                    print("Bayes net initialization error")
                    print("Factor scope {} has variable {} that", end="")
                    print(
                        " does not appear in list of variables {}.".format(
                            (
                                list(map(lambda x: x.name, f.get_scope())),
                                v.name,
                                list(map(lambda x: x.name, Vars)),
                            )
                        )
                    )

    def factors(self):
        return list(self.Factors)

    def variables(self):
        return list(self.Variables)


def name_factor(scope: List[Variable]):
    if len(scope) == 0:
        return "Constant"
    elif len(scope) == 1:
        factor_name = f"P({scope[0].name})"
    else:
        factor_name = f"P({scope[0].name}|{','.join(v.name for v in scope[1:])})"
    return factor_name


def get_possible_combinations(scope: List[Variable]):
    domains = [v.domain() for v in scope]
    return product(*domains)


def multiply_factors(Factors: List[Factor]) -> Factor:
    """return a new factor that is the product of the factors in Fators"""
    # IMPLEMENT
    if len(Factors) == 1:
        return Factors[0]
    factor, rest = Factors[0], Factors[1:]
    rest_factor = multiply_factors(rest)
    factor_scope, rest_scope = set(factor.get_scope()), set(rest_factor.get_scope())

    # the total scope is the union of both scopes
    total_scope: List[Variable] = list(factor_scope | rest_scope)
    # sort variables by name to preserve reproducibility
    total_scope.sort(key=lambda v: v.name)

    # find the index that corresponds to either factor so we can look up the value
    factor_i = [total_scope.index(v) for v in factor.get_scope()]
    rest_i = [total_scope.index(v) for v in rest_factor.get_scope()]

    new_factor = Factor(name_factor(total_scope), total_scope)
    new_factor_values = []

    for vals in get_possible_combinations(total_scope):
        factor_val = factor.get_value([vals[i] for i in factor_i])
        rest_val = rest_factor.get_value([vals[i] for i in rest_i])
        new_factor_values.append([*vals, factor_val * rest_val])
    new_factor.add_values(new_factor_values)
    return new_factor


def restrict_factor(f: Factor, var: Variable, value):
    """f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor"""
    # IMPLEMENT
    scope = f.get_scope()
    i = scope.index(var)
    other_i = [j for j in range(len(scope)) if j != i]
    values = []
    for vals in get_possible_combinations(scope):
        if vals[i] == value:
            values.append([*(vals[j] for j in other_i), f.get_value(vals)])
    scope.pop(i)
    factor = Factor(name_factor(scope), scope)
    factor.add_values(values)
    return factor


def sum_out_variable(f: Factor, var: Variable):
    """return a new factor that is the product of the factors in Factors
       followed by the suming out of Var"""
    # IMPLEMENT
    scope = f.get_scope()
    i = scope.index(var)
    values = []
    scope.pop(i)
    for vals in get_possible_combinations(scope):
        marginal_sum = 0
        for v in var.domain():
            combined_vals = list(vals)
            combined_vals.insert(i, v)
            marginal_sum += f.get_value(combined_vals)
        values.append([*vals, marginal_sum])
    factor = Factor(name_factor(scope), scope)
    factor.add_values(values)
    return factor


def normalize(nums):
    """take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers"""
    s = sum(nums)
    if s == 0:
        newnums = [0] * len(nums)
    else:
        newnums = []
        for n in nums:
            newnums.append(n / s)
    return newnums


def rounded(l):
    return [round(n, 4) for n in l]


###Orderings
def min_fill_ordering(Factors, QueryVar):
    """Compute a min fill ordering given a list of factors. Return a list
    of variables from the scopes of the factors in Factors. The QueryVar is 
    NOT part of the returned ordering"""
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
    """Given a set of scopes (lists of lists of variables) compute and
    return the variable with minimum fill in. That the variable that
    generates a factor of smallest scope when eliminated from the set
    of scopes. Also return the new scope generated from eliminating
    that variable."""
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
    """Return the fill in scope generated by eliminating var from
    scopes along with the size of this new scope"""
    union = []
    for s in scopes:
        if var in s:
            for v in s:
                if not v in union:
                    union.append(v)
    if var in union:
        union.remove(var)
    return (len(union), union)


def remove_var(var, new_scope, scopes):
    """Return the new set of scopes that arise from eliminating var
    from scopes"""
    new_scopes = []
    for s in scopes:
        if not var in s:
            new_scopes.append(s)
    new_scopes.append(new_scope)
    return new_scopes


def partition_factors(factors: List[Factor], var: Variable):
    remaining, containing = [], []
    for f in factors:
        if var in f.get_scope():
            containing.append(f)
        else:
            remaining.append(f)
    return remaining, containing


###
def VE(Net: BN, QueryVar: Variable, EvidenceVars: List[Variable]):
    """
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
    """
    # IMPLEMENT
    factors: List[Factor] = Net.factors()
    # variables: Set[Variable] = set(Net.variables())

    # apply evidence
    for e in EvidenceVars:
        # variables.discard(e)
        factors, relevant_factors = partition_factors(factors, e)
        for f in relevant_factors:
            # ignore constant factors and evidence-only factors
            if len(f.get_scope()) <= 1:
                continue
            factors.append(restrict_factor(f, e, e.get_evidence()))
    # total_scope = set()
    # total_scope.update(*(f.get_scope() for f in factors))
    # assert set(variables) == total_scope

    # now all evidence has been applied, eliminate remaining variables
    for var in min_fill_ordering(factors, QueryVar):
        factors, relevant_factors = partition_factors(factors, var)
        summed = sum_out_variable(multiply_factors(relevant_factors), var)
        factors.append(summed)

    last_factor = multiply_factors(factors)
    return rounded(normalize(last_factor.values))


if __name__ == "__main__":

    # testing multiplying factors
    A = Variable("A", ["a", "-a"])
    B = Variable("B", ["b", "-b"])
    C = Variable("C", ["c", "-c"])
    fab = Factor("AB", [A, B])
    fbc = Factor("BC", [B, C])
    fab.add_values(
        [["a", "b", 0.9], ["a", "-b", 0.1], ["-a", "b", 0.4], ["-a", "-b", 0.6],]
    )
    fbc.add_values(
        [["b", "c", 0.7], ["b", "-c", 0.3], ["-b", "c", 0.8], ["-b", "-c", 0.2],]
    )
    fabc = multiply_factors([fab, fbc])
    # fab.print_table()
    # fbc.print_table()
    # fabc.print_table()
    assert rounded(fabc.values) == [
        0.63,
        0.27,
        0.08,
        0.02,
        0.28,
        0.12,
        0.48,
        0.12,
    ]
    # testing restricting
    fbaa = restrict_factor(fab, A, "a")
    # fbaa.print_table()
    assert fbaa.values == [0.9, 0.1]

    # testing summing out variable
    fb = sum_out_variable(fab, A)
    # fb.print_table()
    assert fb.values == [1.3, 0.7]

    # multi factor test
    f1 = Factor("A", [A])
    f1.add_values([["a", 0.9], ["-a", 0.1]])
    f2 = Factor("AB", [A, B])
    f2.add_values(
        [["a", "b", 0.9], ["a", "-b", 0.1], ["-a", "b", 0.4], ["-a", "-b", 0.6]]
    )
    f3 = Factor("BC", [B, C])
    f3.add_values(
        [["b", "c", 0.7], ["b", "-c", 0.3], ["-b", "c", 0.2], ["-b", "-c", 0.8],]
    )
    f4 = sum_out_variable(multiply_factors([f1, f2]), A)
    assert rounded(f4.values) == [0.85, 0.15]
    f5 = sum_out_variable(multiply_factors([f3, f4]), B)
    assert rounded(f5.values) == [0.625, 0.375]
