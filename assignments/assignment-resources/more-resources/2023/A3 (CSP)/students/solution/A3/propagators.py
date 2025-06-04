#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented.

##JNOTE: This is exactly the code Fahiem gave me last term

'''
This file will contain different constraint propagators to be used within
bt_search.

propagator == a function with the following template
    propagator(csp, newly_instantiated_variable=None)
        ==> returns (True/False, [(Variable, Value), (Variable, Value) ...])

    csp is a CSP object---the propagator can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    newly_instaniated_variable is an optional argument.
    if newly_instantiated_variable is not None:
        then newly_instantiated_variable is the most
        recently assigned variable of the search.
    else:
        propagator is called before any assignments are made
        in which case it must decide what processing to do
        prior to any variables being assigned. SEE BELOW

    The propagator returns True/False and a list of (Variable, Value) pairs.

    Returns False if a deadend has been detected by the propagator.
        in this case bt_search will backtrack
    Returns True if we can continue.

    The list of variable values pairs are all of the values
    the propagator pruned (using the variable's prune_value method).
    bt_search NEEDS to know this in order to correctly restore these
    values when it undoes a variable assignment.

    NOTE propagator SHOULD NOT prune a value that has already been
    pruned! Nor should it prune a value twice

    PROPAGATOR called with newly_instantiated_variable = None
        PROCESSING REQUIRED:
            for plain backtracking (where we only check fully instantiated
            constraints) we do nothing...return (true, [])

            for forward checking (where we only check constraints with one
            remaining variable) we look for unary constraints of the csp
            (constraints whose scope contains only one variable) and we
            forward_check these constraints.

            for gac we establish initial GAC by initializing the GAC queue with
            all constaints of the csp

    PROPAGATOR called with newly_instantiated_variable = a variable V
        PROCESSING REQUIRED:
            for plain backtracking we check all constraints with V (see csp
            method get_cons_with_var) that are fully assigned.

            for forward checking we forward check all constraints with V that
            have one unassigned variable left

            for gac we initialize the GAC queue with all constraints containing
            V.
'''

def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []

def prop_FC(csp, newVar=None):
    '''Do forward checking.  That is, check constraints with only one
    uninstantiated variable, and prune appropriately.  (i.e., do not prune a
    value that has already been pruned; do not prune the same value twice.)
    Return if a deadend has been detected, and return the variable/value pairs
    that have been pruned.  See beginning of this file for complete description
    of what propagator functions should take as input and return.

    Input: csp, (optional) newVar.
        csp is a CSP object---the propagator uses this to
        access the variables and constraints.

        newVar is an optional argument.
        if newVar is not None:
            then newVar is the most recently assigned variable of the search.
        else:
            propagator is called before any assignments are made in which case
            it must decide what processing to do prior to any variable
            assignment.

    Returns: (boolean,list) tuple, where list is a list of tuples:
             (True/False, [(Variable, Value), (Variable, Value), ... ])

        boolean is False if a deadend has been detected, and True otherwise.

        list is a set of variable/value pairs that are all of the values the
        propagator pruned.
    '''

    cons_to_check = []
    if not newVar:
        #check all constraints propagate constraints with single variables
        cons_to_check = csp.get_all_cons()  
    else:
        #check constraints with new var
        cons_to_check = csp.get_cons_with_var(newVar)
    #print("FC checking newVar", newVar, end='')
    #if newVar:
    #    print('=', newVar.get_assigned_value())
    #print()

    prunings = []

    for c in cons_to_check:
        if c.get_n_unasgn() == 1:
            uvar = c.get_unasgn_vars()[0]
            status = forward_check(c, uvar, prunings)
            if not status:   #found DWO
                return False, prunings

    #all constraint forward checked, no DWO found.
    return True, prunings

def forward_check(con, uvar, prunings):
    '''Auxilary routine to forward check one constraint
       augment prunings with info about any pruned values
       return false is we find a variable with a DWO.
       return true otherwise'''

    #print("forward_check(", con, ",", uvar, ")")
    vals = []
    #Set up value list in same order as scope of con 
    uvar_index = 0
    for i, var in enumerate(con.get_scope()):
        if var.is_assigned():
            vals.append(var.get_assigned_value())
        else:
            uvar_index = i
            vals.append(None)

    #Now check all values of uvar
    for val in uvar.cur_domain():
        vals[uvar_index] = val
        if not con.check(vals):
            prunings.append((uvar, val))
            uvar.prune_value(val)


    #print("After forward check")
    #print(uvar)
    #print("Prunings = ", prunings)

    if uvar.cur_domain_size() == 0:
        return False
    else:
        return True

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation, as described in lecture. See beginning of this file
    for complete description of what propagator functions should take as input
    and return.

    Input: csp, (optional) newVar.
        csp is a CSP object---the propagator uses this to access the variables
        and constraints.

        newVar is an optional argument.
        if newVar is not None:
            do GAC enforce with constraints containing newVar on the GAC queue.
        else:
            Do initial GAC enforce, processing all constraints.

    Returns: (boolean,list) tuple, where list is a list of tuples:
             (True/False, [(Variable, Value), (Variable, Value), ... ])

    boolean is False if a deadend has been detected, and True otherwise.

    list is a set of variable/value pairs that are all of the values the
    propagator pruned.
    '''

    GAC_queue = []
    if not newVar:
        GAC_queue = csp.get_all_cons()
    else:
        GAC_queue = csp.get_cons_with_var(newVar)

    prunings = []
    while GAC_queue:
        c = GAC_queue.pop()
        for var in c.get_scope():
            for val in var.cur_domain(): 
                 if not c.has_support(var, val):
                     #print("Pruning", var, val)
                     prunings.append((var, val))
                     var.prune_value(val)
                     if var.cur_domain_size() == 0:
                         return False, prunings
                     for c_var in csp.get_cons_with_var(var):
                         if c_var != c and not c_var in GAC_queue:
                             GAC_queue.append(c_var)
    return True, prunings


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # This breaks ties by using the first element it sees, i.e. the one that is earlier in the var list
    return min(csp.get_all_unasgn_vars(), key=lambda x: x.cur_domain_size())
    
