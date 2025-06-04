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
    if (len(Factors) == 1):
        return Factors[0]
    elif (len(Factors) == 2):
        new_scope = Factors[0].get_scope().copy()
        name = "P(" + new_scope[0].name + "|"
        # New scope of the merged factors
        for i in Factors[1].get_scope():
            if i not in new_scope:
                new_scope.append(i)

        # Set the name for the new factor
        i = 1
        while (i < len(new_scope)):
            if (i == len(new_scope) - 1):
                name = name + new_scope[i].name
            else:
                name = name + new_scope[i].name + ","
            i = i + 1
        name = name + ")"

        return_factor = Factor(name, new_scope)

        # Use helper function to iterate through all possible variable assignments and get the value of that assignment
        # It gets set into the values_list
        values_list = []
        multiply_helper(Factors[0], Factors[1], new_scope, values_list, None)
        return_factor.add_values(values_list)
        return multiply_factors([return_factor])
    else:
        # Merge leftmost 2 factors and then recursive call for the remaining factors
        merged_factor = multiply_factors([Factors[0]] + [Factors[1]])
        return multiply_factors([merged_factor] + Factors[2:])

def multiply_helper(lf, rf, scope, return_list, vars_list):
    # If only one variable left in scope, get the value at the current assignment
    if (len(scope) == 1):
        for var in scope[0].domain():
            scope[0].set_assignment(var)
            temp_list = vars_list.copy()
            value = lf.get_value_at_current_assignments() * rf.get_value_at_current_assignments()
            temp_list.append(var)
            temp_list.append(value)
            return_list.append(temp_list)
    # Recursive call assigns possible value starting with the leftmost variable in the merged_scope
    else:
        for var in scope[0].domain():
            scope[0].set_assignment(var)
            # If the value list has not been created yet, create it and pass it onto the recursive call
            if(vars_list == None):
                temp_list = []
                temp_list.append(var)
                multiply_helper(lf, rf, scope[1:], return_list, temp_list)
            else:
                copied_list = vars_list.copy()
                copied_list.append(var)
                multiply_helper(lf, rf, scope[1:], return_list, copied_list)

def restrict_factor(f, var, value):
    '''f is a factor, var is a Variable, and value is a value from var.domain.
    Return a new factor that is the restriction of f by this var = value.
    Don't change f! If f has only one variable its restriction yields a
    constant factor'''
    # Create new factor and set the values
    if (len(f.get_scope()) == 1):
        name = "P(" + value
    else:
        if (value in f.get_scope()[0].domain()):
            name = "P(" + value + "|"
        else:
            name = "P(" + f.get_scope()[0].name + "|"

    # Set the name for the new factor
    i = 1
    while (i < len(f.get_scope())):
        if (i == len(f.get_scope()) - 1):
            name = name + f.get_scope()[i].name
        else:
            name = name + f.get_scope()[i].name + ","
        i = i + 1
    name = name + ")"

    new_factor = Factor(name, f.get_scope())

    # Get the opposite of value. If it's e then -e. If -e then e
    if "-" in value:
        opposite = value[1:]
    else:
        opposite = "-" + value

    # Value list to be used for input for add_values
    value_list = []
    # Get all the possible values with the restriction
    restrict_helper(f, opposite, f.get_scope(), value_list, None)

    new_factor.add_values(value_list)
    # Loop over scope, if var in scope is the same as var then assign it the value
    for i in f.get_scope():
        if (i == var):
            i.set_assignment(value)
    # Remove opposite of value from value list
    return new_factor

def restrict_helper(f, val, scope, val_list, var_list):
    # If only one variable left in scope, get the value at the current assignment
    if (len(scope) == 1):
        for var in scope[0].domain():
            if (var != val):
                scope[0].set_assignment(var)
                value = f.get_value_at_current_assignments()
                if (var_list == None):
                    var_list = []
                    var_list.append(var)
                    var_list.append(value)
                    val_list.append(var_list.copy())
                    var_list.remove(var)
                    var_list.remove(value)
                else:
                    var_list.append(var)
                    var_list.append(value)
                    val_list.append(var_list.copy())
                    var_list.remove(var)
                    var_list.remove(value)

        #print(val_list)
        #print(var_list)
    # Recursive call assigns possible value starting with the leftmost variable in the scope
    else:
        for var in scope[0].domain():
            # If variable is the opposite of our variable, then ignore it cause the other variable will be set
            # In other words, do not add it to the value list because value is restricted
            if (var != val):
                scope[0].set_assignment(var)
                if(var_list == None):
                    temp_list = []
                    temp_list.append(var)
                    restrict_helper(f, val, scope[1:], val_list, temp_list)
                else:
                    copied_list = var_list.copy()
                    copied_list.append(var)
                    restrict_helper(f, val, scope[1:], val_list, copied_list)

def sum_out_variable(f, var):
    '''return a new factor that is the product of the factors in Factors
       followed by the suming out of Var'''
    new_scope = f.get_scope().copy()
    # Removing the var from the scope. Doesnt work when I just do .remove() for some reason
    for i in new_scope:
        if i == var:
            new_scope.remove(i)
    # Create new factor with the var removed in the scope
    # Set the name for the new factor
    name = "P("
    i = 1
    while (i < len(new_scope)):
        if (i == len(new_scope) - 1):
            name = name + new_scope[i].name
        else:
            name = name + new_scope[i].name + ","
        i = i + 1
    name = name + ")"

    new_factor = Factor(name, new_scope)
    if (len(f.get_scope()) == 1):
        # If there is only one variable in the scope, summing itself is just one
        new_factor.add_value_at_current_assignment(1)
        return new_factor
    else:
        # Get the assignments for both possible values of the variable (Only works if there are only 2 values in its domain)

        # Code that is commented out is the part that only worked with 2 variables in the domain. Now it works with all of them :)

        # value_list = []
        # var.set_assignment(var.domain()[0])
        # sum_helper(f, new_scope, value_list, None)
        # # Other side
        # value_list_opposite = []
        # var.set_assignment(var.domain()[1])
        # sum_helper(f, new_scope, value_list_opposite, None)
        # # Initialize list to be returned
        # return_list = []
        # count = 0
        # # Sum out the variable from the lists above
        # while (count < len(value_list)):
        #     temp_list = value_list[count].copy()
        #     temp_list[-1] = value_list[count][-1] + value_list_opposite[count][-1]
        #     return_list.append(temp_list)
        #     count = count + 1

        temp_list = []
        for variable in var.domain():
            var.set_assignment(variable)
            sum_helper(f, new_scope, temp_list, None)

        length = int(len(temp_list)/len(var.domain()))
        first_list = temp_list[:length]

        count = length
        while (count < len(temp_list)):
            i = 0
            while (i < length):
                first_list[i][-1] = first_list[i][-1] + temp_list[count + i][-1]
                i = i+1
            count = count + length
        # # Then add it to the new factor
        new_factor.add_values(first_list)
    return new_factor

def sum_helper(f, scope, val_list, var_list):
    # If only one variable left in scope, get value at current assignment and add to value list
    if (len(scope) == 1):
        for var in scope[0].domain():
            scope[0].set_assignment(var)
            value = f.get_value_at_current_assignments()
            if (var_list == None):
                var_list = []
                var_list.append(var)
                var_list.append(value)
                val_list.append(var_list.copy())
                var_list.remove(var)
                var_list.remove(value)
            else:
                var_list.append(var)
                var_list.append(value)
                val_list.append(var_list.copy())
                var_list.remove(var)
                var_list.remove(value)

    # Recursive call assigns value starting with the leftmost variable
    else:
        for var in scope[0].domain():
            # Set assignment and recursive call remaining scope
            scope[0].set_assignment(var)
            if (var_list == None):
                temp_list = []
                temp_list.append(var)
                sum_helper(f, scope[1:], val_list, temp_list)
            else:
                copied_list = var_list.copy()
                copied_list.append(var)
                sum_helper(f, scope[1:], val_list, copied_list)

def normalize(nums):
    '''take as input a list of number and return a new list of numbers where
    now the numbers sum to 1, i.e., normalize the input numbers'''
    sum = 0
    for i in nums:
        sum = sum + i
    # Get some above then normalize
    return_list = []
    for i in nums:
        if sum == 0:
            return_list.append(0)
        else:
            return_list.append(i/sum)
    return return_list

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
    # Replace factors that mention some evidence variable
    factors_copy = Net.factors().copy()
    for factor in factors_copy:
        for var in EvidenceVars:
            if var in factor.get_scope():
                # If factor's scope contains a restricted factor, create a new factor with that variable restricted
                new_factor = restrict_factor(factor, var, var.get_evidence())
                index = factors_copy.index(factor)
                # Remove old factor and add new factor at same index
                factors_copy.remove(factor)
                factors_copy.insert(index, new_factor)
                factor = new_factor
    #test = 0
    # Multiply the factors together and get the minimum fill ordering
    multiplied_factor = multiply_factors(factors_copy)
    min_fill = min_fill_ordering([multiplied_factor], QueryVar)
    new_factor = multiplied_factor
    # Sum out the factor based on the minimum fill ordering
    for j in min_fill:
        new_factor = sum_out_variable(new_factor, j)

    # assign values then get the probability and normalize
    prob = []
    for var in (QueryVar.domain()):
        QueryVar.set_assignment(var)
        prob.append(new_factor.get_value_at_current_assignments())
    return_prob = normalize(prob)

    return return_prob
