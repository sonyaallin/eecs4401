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
        self.name = name  # text name for variable
        self.dom = list(domain)  # Make a copy of passed domain
        # evidence value (stored as index into self.dom)
        self.evidence_index = 0
        self.assignment_index = 0  # For use by factors. We can assign variables values
        # and these assigned values can be used by factors
        # to index into their tables.

    def add_domain_values(self, values):
        '''Add domain values to the domain. values should be a list.'''
        for val in values:
            self.dom.append(val)

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

    def set_evidence(self, val):
        '''set this variable's value when it operates as evidence'''
        self.evidence_index = self.value_index(val)

    def get_evidence(self):
        return(self.dom[self.evidence_index])

    def set_assignment(self, val):
        '''Set this variable's assignment value for factor lookups'''
        self.assignment_index = self.value_index(val)

    def get_assignment(self):
        return(self.dom[self.assignment_index])

    # These routines are special low-level routines used directly by the
    # factor objects
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
        self.values = [0]*size  # initialize values to be long list of zeros.

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
                    print(" does not appear in list of variables {}.".format(list(
                        map(lambda x: x.name, f.get_scope())), v.name, list(map(lambda x: x.name, Vars))))

    def factors(self):
        return list(self.Factors)

    def variables(self):
        return list(self.Variables)


# ----------------------------------------------------------------------------
# helper functions
# ----------------------------------------------------------------------------


def get_factor_by_dict(name: str, scope: list, d_values: dict) -> Factor:
    f = Factor(name, scope)
    for k, v in d_values.items():
        f.add_values([list(k)+[v]])
    return f


def make_domains_list(scope: list, domains: list, domains_size: list) -> None:
    domains.clear()
    domains_size.clear()
    for var in scope:
        domains.append(var.domain())
        domains_size.append(var.domain_size()-1)


def construct_factor_items(combination_count: list, domains_size: list, assign_value, add_item) -> None:
    """construct the factor by traversal of the domain space.

    Args:
        combination_count (list): indices for the values in each domain
        domains_size (list): upper bound of indices in each domain
        assign_value ([function]): the nested function to make the ith value set
        add_item ([function]): the nested function to create and add the item
    """
    max_depth: int = len(domains_size) - 1
    depth_pointer: int = max_depth

    if max_depth == -1:
        add_item()
        return

    while True:
        # initialize the value assignment
        for i in range(depth_pointer):
            assign_value(i)
        # save "if depth_pointer == max_depth:"
        while combination_count[depth_pointer] <= domains_size[depth_pointer]:
            assign_value(depth_pointer)
            add_item()
            combination_count[depth_pointer] += 1
        # check if exit
        exit_flag = True
        for i in range(depth_pointer):
            if combination_count[i] != domains_size[i]:
                exit_flag = False
                break
        if exit_flag:
            break
        # because of the check of exit above, will not have a exceeding backtracking case
        # so we can save a condition "and depth_pointer > 0"
        while combination_count[depth_pointer] > domains_size[depth_pointer]:
            combination_count[depth_pointer] = 0
            depth_pointer -= 1
            combination_count[depth_pointer] += 1

        # reset depth_pointer
        depth_pointer = max_depth


# ----------------------------------------------------------------------------
# to implement
# ----------------------------------------------------------------------------


def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Fators'''
    # I use a dict here rather than linear arrays because I am afraid that
    # some combinations of variables' value in their domains don't have an
    # assigned value from the input factors.
    # list structure should be faster, but only works well when the inputs
    # are regular. To make the program more robust here dict is chosen.

    # Looking at the given code above, it doesn't handle this case. It just
    # initialize every possible output to be zero at first. So we can safely
    # assume all the input will be valid and regular. However it was late
    # when I recognized this. I don't want to rewrite these functions so
    # I left the dicts here.

    product: dict = {}
    temp_product: dict = {}

    scope: list = []  # List[Variable]
    domains = []  # List[list]
    domains_size = []  # List[int]

    first_factor = True

    for f in Factors:
        diff_scope: list = []  # List[Variable]
        scope_size: int = len(scope)
        old_scope_size = scope_size
        new_vars_index = []  # List[int]

        for var in f.get_scope():
            found_flag = False
            for i in range(len(scope)):
                if scope[i] == var:
                    found_flag = True
                    new_vars_index.append(i)
                    break
            if found_flag == False:
                diff_scope.append(var)
                new_vars_index.append(scope_size)
                scope_size += 1

        scope += diff_scope
        if len(scope) == 0:
            continue
        make_domains_list(scope, domains, domains_size)

        # use iteration instead of recursion
        combination_count = [0]*len(domains_size)  # List[int]

        old_tuple_list = [None]*old_scope_size
        new_tuple_list = [None]*scope_size

        def assign_value(index: int) -> None:
            nonlocal combination_count, domains, domains_size, scope
            nonlocal old_tuple_list, new_tuple_list, old_scope_size, new_vars_index
            if domains_size[index] >= 0:
                value = domains[index][combination_count[index]]
                new_tuple_list[index] = value
                if index < old_scope_size:
                    old_tuple_list[index] = value
                if index in new_vars_index:
                    scope[index].set_assignment(value)

        def add_product() -> None:
            nonlocal product, temp_product, old_tuple_list, f, new_tuple_list, first_factor
            old_value = product.get(tuple(old_tuple_list), None)
            new_value = f.get_value_at_current_assignments()
            if old_value != None:
                temp_product[tuple(new_tuple_list)] = old_value * new_value
            elif first_factor == True:
                temp_product[tuple(new_tuple_list)] = new_value

        construct_factor_items(
            combination_count, domains_size, assign_value, add_product)

        product = temp_product
        temp_product = {}
        first_factor = False

    return get_factor_by_dict("product", scope, product)


def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    scope = []

    found_flag = False
    for i in f.get_scope():
        if i == var:
            found_flag = True
        else:
            scope.append(i)
    if found_flag == False:
        return f  # error case when var is not in original scope

    new_factor = Factor("restrict", scope)

    domains = []
    domains_size = []
    combination_count = [0]*len(scope)
    make_domains_list(scope, domains, domains_size)

    # initialize the restrict
    var.set_assignment(value)

    def assign_value(index: int) -> None:
        nonlocal combination_count, domains, domains_size, scope
        if domains_size[index] >= 0:
            value = domains[index][combination_count[index]]
            scope[index].set_assignment(value)

    def add_restrict() -> None:
        nonlocal new_factor, f
        value = f.get_value_at_current_assignments()
        new_factor.add_value_at_current_assignment(value)

    construct_factor_items(combination_count, domains_size,
                           assign_value, add_restrict)
    return new_factor


def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    scope = []

    found_flag = False
    for i in f.get_scope():
        if i == var:
            found_flag = True
        else:
            scope.append(i)
    if found_flag == False:
        return f  # error case when var is not in original scope

    new_factor = Factor("sumout", scope)

    domains = []
    domains_size = []
    combination_count = [0]*len(scope)
    make_domains_list(scope, domains, domains_size)

    # initialize the sum out domain
    sum_out_domain = var.domain()

    def assign_value(index: int) -> None:
        nonlocal combination_count, domains, domains_size, scope
        if domains_size[index] >= 0:
            value = domains[index][combination_count[index]]
            scope[index].set_assignment(value)

    def add_summout() -> None:
        nonlocal new_factor, f, var, sum_out_domain
        value_sum = 0
        for i in sum_out_domain:
            var.set_assignment(i)
            value_sum += f.get_value_at_current_assignments()
        new_factor.add_value_at_current_assignment(value_sum)

    construct_factor_items(combination_count, domains_size,
                           assign_value, add_summout)
    return new_factor


def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''
    total_sum = 0
    new_list = []
    for n in nums:
        total_sum += n

    if total_sum == 0:
        return nums  # cannot normalize

    for n in nums:
        new_list.append(n / total_sum)

    return new_list

# Orderings


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
    if var in union:
        union.remove(var)
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

    # the algorithm is from the slides
    # ---------------------------------------------------------------------------- #
    #  replace each factor with its restriction of evidence
    factors = Net.factors()  # List[Factor]
    new_factors = []  # List[Factor]

    for f in factors:
        temp_f: Factor = f
        for e in EvidenceVars:  # List[Variable]
            temp_f = restrict_factor(temp_f, e, e.get_evidence())
        new_factors.append(temp_f)

    # renew
    factors = new_factors
    new_factors = []

    # ---------------------------------------------------------------------------- #
    # eliminate remaining vars Z
    variables = min_fill_ordering(factors, QueryVar)
    for v in variables:
        multiply_list = []  # List[Factor]
        for f in factors:
            if v in f.get_scope():
                multiply_list.append(f)
            else:
                new_factors.append(f)
        factors = new_factors
        new_factors = []
        multiply_result: Factor = multiply_factors(multiply_list)
        factors.append(sum_out_variable(multiply_result, v))

    # ---------------------------------------------------------------------------- #
    # take product and normalize to get P(Q|E)
    product: Factor = multiply_factors(factors)
    result = []
    for i in range(QueryVar.domain_size()):
        QueryVar.set_assignment_index(i)
        result.append(product.get_value_at_current_assignments())

    return normalize(result)
