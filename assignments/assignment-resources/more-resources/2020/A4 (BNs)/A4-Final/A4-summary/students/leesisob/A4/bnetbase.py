import itertools 

class Variable:    
    def __init__(self, name, domain=[]):
        self.name = name                #text name for variable
        self.dom = list(domain)         #Make a copy of passed domain
        self.evidence_index = 0         #evidence value (stored as index into self.dom)
        self.assignment_index = 0       #For use by factors. We can assign variables values
                                        #and these assigned values can be used by factors
                                        #to index into their tables.
    def add_domain_values(self, values):
        for val in values: self.dom.append(val)

    def value_index(self, value):
        return self.dom.index(value)

    def domain_size(self):
        return(len(self.dom))

    def domain(self):
        return(list(self.dom))

    def set_evidence(self,val):
        self.evidence_index = self.value_index(val)

    def get_evidence(self):
        return(self.dom[self.evidence_index])

    def set_assignment(self, val):
        self.assignment_index = self.value_index(val)

    def get_assignment(self):
        return(self.dom[self.assignment_index])
    ##These routines are special low-level routines used directly by factor objects
    def set_assignment_index(self, index):
        self.assignment_index = index
        
    def get_assignment_index(self):
        return(self.assignment_index)

    def __repr__(self):
        return("{}".format(self.name))
    
    def __str__(self):
        return("{}, Dom = {}".format(self.name, self.dom))


class Factor: 
    def __init__(self, name, scope):
        self.scope = list(scope)
        self.name = name
        size = 1
        for v in scope:
            size = size * v.domain_size()
        self.values = [0]*size  #initialize values to be long list of zeros.

    def get_scope(self):
        return list(self.scope)

    def add_values(self, values):
        for t in values:
            index = 0
            for v in self.scope:
                index = index * v.domain_size() + v.value_index(t[0])
                t = t[1:]
            self.values[index] = t[0]
         
    def add_value_at_current_assignment(self, number): 
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        self.values[index] = number

    def get_value(self, variable_values):
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.value_index(variable_values[0])
            variable_values = variable_values[1:]
        return self.values[index]

    def get_value_at_current_assignments(self):        
        index = 0
        for v in self.scope:
            index = index * v.domain_size() + v.get_assignment_index()
        return self.values[index]

    def print_table(self):
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
    new_scope = []
    new_name = ''

    factor_vars_indices = [[] for i in range(len(Factors))]
    for f in range(len(Factors)):
        new_name = new_name + '*' + Factors[f].name
        for var in Factors[f].get_scope():
            if var not in new_scope:
                new_scope += [var]
            factor_vars_indices[f] += [new_scope.index(var)]
            
    domains = [var.dom for var in new_scope]
    poss = list(itertools.product(*domains))
    
    new_values = [1]*len(poss)
    for i in range(len(poss)):
        for f in range(len(Factors)):
            f_assign = [poss[i][v] for v in factor_vars_indices[f]] 
            new_values[i] = new_values[i]*Factors[f].get_value(f_assign)
            
    new_Factor = Factor(new_name, new_scope)
    new_Factor.values = new_values
    return new_Factor

def restrict_factor(f, var, value):
    v_i = f.get_scope().index(var)
    new_scope = f.get_scope()[0:v_i]+f.get_scope()[v_i+1:]
    d_i = var.dom.index(value)
    new_name = f.name+" restricted by "+str(var.name)+" = "+str(value)
    new_Factor = Factor(new_name, new_scope)
    
    skip = 1
    for v in f.get_scope()[v_i:]:
        skip = skip*v.domain_size()
    
    length = skip//var.domain_size()
    index = length*d_i
    
    new_values = []
    while index < len(f.values):
        for i in range(length):
            new_values.append(f.values[index+i])
        index = index+skip
    
    new_Factor.values = new_values
    return new_Factor


def sum_out_variable(f, var):
    v_i = f.get_scope().index(var)
    new_scope = f.get_scope()[0:v_i]+f.get_scope()[v_i+1:]
    new_name = f.name + ', Sum out: ' + str(var.name)
    new_Factor = Factor(new_name, new_scope)
    
    domains = [var.dom for var in new_scope]
    poss = list(itertools.product(*domains))
    
    new_values = []
    for assignment in poss:
        acc = 0
        for val in var.dom:
            old_assign = list(assignment)
            old_assign.insert(v_i,val)
            acc = acc + f.get_value(old_assign)
        new_values.append(acc)
    
    new_Factor.values = new_values 
    return new_Factor


def normalize(nums):
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
    curr_factors = Net.factors()
    set_vars = []
    remain_vars = []
    set_values = []
    for var in EvidenceVars:
        set_vars.append(var)
        set_values.append(var.get_evidence())
        
    for f in range(len(curr_factors)):
        initial_scope = curr_factors[f].get_scope()
        for f_var in initial_scope:
            if f_var in set_vars:
                curr_factors[f] = restrict_factor(curr_factors[f], f_var, set_values[set_vars.index(f_var)])
                if curr_factors[f].get_scope() == [QueryVar]:
                    new_values = normalize(curr_factors[f].values)
                    return new_values
            elif f_var not in remain_vars:
                if f_var != QueryVar:
                    remain_vars.append(f_var)
    
    curr_factors = [factor for factor in curr_factors if len(factor.get_scope())!=0]
    
    remain_vars = min_fill_ordering(curr_factors, QueryVar)
                
    for var in remain_vars:
        Factors = []
        initial_factors = curr_factors.copy()
        for factor in initial_factors:
            if var in factor.get_scope():
                curr_factors.remove(factor)
                Factors.append(factor)
        if len(Factors) > 0:
            new_factor = multiply_factors(Factors)
            new_factor = sum_out_variable(new_factor,var)
            curr_factors.append(new_factor)
        
    final_factor = multiply_factors(curr_factors)    
    new_values = normalize(final_factor.values)
    return new_values
