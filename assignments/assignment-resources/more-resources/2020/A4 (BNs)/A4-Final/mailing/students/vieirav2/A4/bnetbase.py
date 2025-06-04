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

def multiply_factors(Factors):
    '''return a new factor that is the product of the factors in Fators'''

    if len(Factors) < 2:
    	product = Factor('Product', Factors[0].get_scope())
    	product.values = list(Factors[0].values)
    	return product

    elif len(Factors) == 2:

        first_factor = Factors[0]
        second_factor = Factors[1]
        var_union = []


        for var in list(first_factor.scope + second_factor.scope):
            if var not in var_union:
                var_union.append(var)

        # print('var_union: {}'.format(var_union))

        product = Factor('Product', var_union)


        # calculating and adding numbers for all possible assignments of values
        #print('first factor: {}'.format(first_factor))
        #print('second factor: {}'.format(second_factor))

        if not first_factor.scope:
            if not second_factor.scope:
                product.add_values([[first_factor.get_value([])*second_factor.get_value([])]])
                return product
            else:
                values = list(second_factor.values)
                # print('2ndvalues: {}'.format(values))
                # print('first_factor.get_value([]): {}'.format(first_factor.get_value([])))
                for i in range(len(values)):
                	# print('value antes: {}'.format(values[i]))
                	# print('multiplier: {}'.format(first_factor.get_value([])))
                	values[i] = values[i] * first_factor.get_value([])
                	# print('value depois:{}'.format(values[i]))
                # print('values: {}'.format(values))
                product.values = values
                return product
        if not second_factor.scope:
            values = list(first_factor.values)
            for i in range(len(values)):
                values[i] = values[i] * second_factor.get_value([])
            product.values = values
            return product


         # saving legacy assignment for each variable
        saved_values_1 = []
        for v in first_factor.scope:
            saved_values_1.append(v.get_assignment_index())
        saved_values_2 = []
        for v in second_factor.scope:
            saved_values_2.append(v.get_assignment_index())

        domains = []
        for var in product.scope:
            domains.append(var.domain())

        possible_assignments = list(itertools.product(*domains))
        # print('assignments: {}'.format(possible_assignments))
        for assignment in possible_assignments:
            # first assigning original factors
            # i = 0
            # for var in product.scope:
            #     if var in first_factor.scope:
            # ...
            # 	var.set_assignment(assignment[i])
            # 	i += 1
            # assigning product variables
            i = 0
            for var in product.scope:
                var.set_assignment(assignment[i])
                i += 1

            # assumindo first and second factors share vars objs with product
            # se isso nao der certo vamos ter q assghment first e second_factors como no comonetario de 362 a 369
            first_number = first_factor.get_value_at_current_assignments()
            second_number = second_factor.get_value_at_current_assignments()
            product.add_value_at_current_assignment(first_number * second_number)


        # restoring legacy assignment for each variable
        for v in first_factor.scope:
            v.set_assignment_index(saved_values_1[0])
            saved_values_1 = saved_values_1[1:]
        for v in second_factor.scope:
            v.set_assignment_index(saved_values_2[0])
            saved_values_2 = saved_values_2[1:]

        return product

    else:           # More than 2 factors to be multiplied
        product = multiply_factors([multiply_factors(Factors[0:2]), multiply_factors(Factors[2:])])
        return product





def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''

    new_scope = f.get_scope()
    if var in new_scope:
    	new_scope.remove(var)

    restricted = Factor('Restricted', new_scope)

    if var not in f.scope:
    	restricted.values = list(f.values)
    	return restricted

    if not restricted.scope:

    	saved_value = var.get_assignment()
    	
    	var.set_assignment(value)
    	constant_number = f.get_value_at_current_assignments()
    	restricted.add_values([[constant_number]])
    	
    	var.set_assignment(saved_value)

    	return restricted


    domains = []
    for _var in f.get_scope():
        domains.append(_var.domain())
    possible_assignments = list(itertools.product(*domains))

    # copying factor table for every possible assignment in f
    new_values = []
    for assignment in possible_assignments:
    	ass = list(assignment)
    	new_values.append( ass + [f.get_value(ass)])

    #print('initial new_values: {}'.format(new_values))
    #print('f.get_scope(): {}'.format(f.get_scope()))
    #print('var: {}'.format(var))

    # Finding index of restricted variable
    index = 0
    for v in f.get_scope():
        if v == var:
            break
        index += 1
    #print('index: {}'.format(index))

    # removing incompatible elements from values
    incompatible_elements = []
    for val in new_values:
    	if val[index] != value:
    		incompatible_elements.append(val)
    for e in incompatible_elements:
    	new_values.remove(e)

    
    # adjusting the remaining elements to not display
    # the redundant value (column) of the fixed variable
    for val in new_values:
    	val.remove(val[index])

    restricted.add_values(new_values)

    #print('restricted: {}'.format(restricted.values))

    return restricted




def sum_out_variable(f, var):
    '''return a new factor that is the suming out of Var'''
    
    new_scope = f.get_scope()
    if var in new_scope:
    	new_scope.remove(var)

    summed = Factor('Summed', new_scope)

    if var not in f.scope:
        summed.values = list(f.values)
        return summed 


    if not summed.scope:

    	saved_value = var.get_assignment()

    	summed_constant_number = 0
    	for _val in var.dom:
    		var.set_assignment(_val)
    		summed_constant_number += f.get_value_at_current_assignments()
    	summed.add_values([[summed_constant_number]])
    	
    	var.set_assignment(saved_value)

    	return summed

    domains = []
    for _var in f.get_scope():
        domains.append(_var.domain())
    possible_assignments = list(itertools.product(*domains))
    #print('possible_assignments: {}'.format(possible_assignments))

    # Finding index of variable to be summed-out
    index = 0
    for v in f.get_scope():
        if v == var:
            break
        index += 1
    #print('index: {}'.format(index))

    # creating tuples with 1) every possible assignment in f
    # except for the column of the variable to be summed-out
    # and 2) its respective result value
    values_tuples = []
    for assignment in possible_assignments:
    	ass = list(assignment)
    	#print('ass: {}'.format(ass))
    	ass.remove(ass[index])
    	_tup = (ass, f.get_value(list(assignment)))
    	#print('_tup: {}'.format(_tup))
    	values_tuples.append(_tup)

    #print('values_tuples: {}'.format(values_tuples))

    # summing result values with identical correspondent assignment except for the
    # variable being summed out
    ass_to_summed_values = dict()

    for tup in values_tuples:
    	cur_ass = tuple(tup[0])
    	cur_sum = tup[1]

    	if cur_ass not in ass_to_summed_values:
    		ass_to_summed_values[cur_ass] = cur_sum
    	else:
    		ass_to_summed_values[cur_ass] = ass_to_summed_values[cur_ass] + cur_sum


    # saving legacy assignment for each variable
    saved_values = []
    for v in summed.scope:
        saved_values.append(v.get_assignment_index())


    # populating values for each of the summed factor possible assignments
    for ass_key in ass_to_summed_values:
    	# assigning
    	i = 0
    	for _val in ass_key:
    		summed.scope[i].set_assignment(_val)
    		i += 1
    	# populating the summed result for this assignment
    	summed.add_value_at_current_assignment(ass_to_summed_values[ass_key])

    # restoring legacy assignment for each variable
    for v in summed.scope:
        v.set_assignment_index(saved_values[0])
        saved_values = saved_values[1:]

    return summed



def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''
    _sum = sum(nums)

    if not _sum:
    	return []

    normalized = []

    for num in nums:
    	normalized.append(num/_sum)

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
   
    # Making copies of original CPTs/factors
    cur_Factors = Net.factors()

    #print('\nNow quering: {} with evidence: {}'.format(QueryVar, EvidenceVars))

    #for _f in cur_Factors:
    #    print('factor original: {} scope: {} values: {}'.format(_f.name, _f.scope, _f.values))


    # Finding factors that contain an evidence variable in their scope
    selected_indices = []
    i = 0
    for _factor in cur_Factors:
    	for _var in _factor.scope:
    		if _var in EvidenceVars:
    		    selected_indices.append(i)
    		    break
    	i += 1

    # print('selected_indices: {}'.format(selected_indices))

    # Replacing those factors by their restricted version
    for index in selected_indices:

    	# finding variables to be restricted in the Factor cur_Factors[index]
    	to_restrict = []
    	for _var in EvidenceVars:
    		if _var in cur_Factors[index].scope:
    			to_restrict.append(_var)

    	# restricting each variable at a time and updating cur_Factors[index]
    	for _var in to_restrict:
    		cur_Factors[index] = restrict_factor(cur_Factors[index], _var, _var.get_evidence())

    #for _f in cur_Factors:
    #    print('factor pos restricao: {} scope: {} values: {}'.format(_f.name, _f.scope, _f.values))

    remaining_vars = min_fill_ordering(cur_Factors, QueryVar)

    # Eliminating each variable from each Factor (if it is the case that
    # the factor has that variable in its scope - tested at sum_out_variable()


    # ERRO ESTÁ AQUI, VC TEM QUE MULTIPLICAR ANTES DE SOMAR

    for e_var in remaining_vars:
        #print('eliminando {}'.format(e_var))

        # finding factors to be eliminated
        to_eliminate = []
        for i in range(len(cur_Factors)):
            if e_var in cur_Factors[i].scope:
                to_eliminate.append(cur_Factors[i])

        # calculating product of such factors
        prod_of_elim = multiply_factors(to_eliminate)

        # summing out e_var of such product
        sum_out_of_prod_of_elim = sum_out_variable(prod_of_elim, e_var)

        # adding that resulting factor to our list of factors
        cur_Factors.append(sum_out_of_prod_of_elim)

        # deleting factor that were already eliminated
        for to_delete in to_eliminate:
            cur_Factors.remove(to_delete)


    #for _f in cur_Factors:
    #    print('\n\nfactor pos VE: {} scope: {} values: {}'.format(_f.name, _f.scope, _f.values))

    # Taking the product of the remaining factors:
    final_Factor = multiply_factors(cur_Factors)

    # print('factor multiplicado: {} scope: {} values: {}'.format(final_Factor.name, final_Factor.scope, final_Factor.values))

    # Extracting probabilities for each value QueryVar can take
    probs = []
    for _val in QueryVar.domain():
    	probs.append(final_Factor.get_value([_val]))

    # print('probs: {}'.format(probs))
    # print('normalized probs: {}'.format(normalize(probs)))

    return normalize(probs)





    















