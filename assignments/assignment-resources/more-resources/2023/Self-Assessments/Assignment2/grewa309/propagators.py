# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete problem solution.

'''This file will contain different constraint propagators to be used within
   bt_search.

   propagator == a function with the following template
      propagator(csp, newly_instantiated_variable=None)
           ==> returns (True/False, [(Variable, Value), (Variable, Value) ...]

      csp is a CSP object---the propagator can use this to get access
      to the variables and constraints of the problem. The assigned variables
      can be accessed via methods, the values assigned can also be accessed.

      newly_instaniated_variable is an optional argument.
      if newly_instantiated_variable is not None:
          then newly_instantiated_variable is the most
           recently assigned variable of the search.
      else:
          progator is called before any assignments are made
          in which case it must decide what processing to do
           prior to any variables being assigned. SEE BELOW

       The propagator returns True/False and a list of (Variable, Value) pairs.
       Return is False if a deadend has been detected by the propagator.
       in this case bt_search will backtrack
       return is true if we can continue.

      The list of variable values pairs are all of the values
      the propagator pruned (using the variable's prune_value method).
      bt_search NEEDS to know this in order to correctly restore these
      values when it undoes a variable assignment.

      NOTE propagator SHOULD NOT prune a value that has already been
      pruned! Nor should it prune a value twice

      PROPAGATOR called with newly_instantiated_variable = None
      PROCESSING REQUIRED:
        for plain backtracking (where we only check fully instantiated
        constraints)
        we do nothing...return true, []

        for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope
        contains only one variable) and we forward_check these constraints.

        for gac we establish initial GAC by initializing the GAC queue
        with all constaints of the csp


      PROPAGATOR called with newly_instantiated_variable = a variable V
      PROCESSING REQUIRED:
         for plain backtracking we check all constraints with V (see csp method
         get_cons_with_var) that are fully assigned.

         for forward checking we forward check all constraints with V
         that have one unassigned variable left

         for gac we initialize the GAC queue with all constraints containing V.


var_ordering == a function with the following template
    ord_mrv(csp)
        ==> returns Variable

    csp is a CSP object---the heuristic can use this to get access to the
    variables and constraints of the problem. The assigned variables can be
    accessed via methods, the values assigned can also be accessed.

    var_ordering returns the next Variable to be assigned, as per the definition
    of the heuristic it implements.
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
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var, 
       only check constraints containing newVar'''
    
    # Loop over all constraints inside CSP that have newVar and ONE unintitiated variables
    newVar_to_cons = []
    pruned_values = []

    if(newVar == None):
        newVar_to_cons =  csp.get_all_cons()
    else:    
        newVar_to_cons = csp.get_cons_with_var(newVar)

    for cons in newVar_to_cons:
        if (cons.get_n_unasgn() == 1):
            # We can prune the domain for the one unassigned variable in this constraint
            unassigned_var = cons.get_unasgn_vars()[0] # we know there is only 1 unassigned var
            var_to_values = [var.get_assigned_value() for var in cons.get_scope()]
            unassigned_var_index = var_to_values.index(None)
            unassigned_var_curr_domain = unassigned_var.cur_domain()

            for value in unassigned_var_curr_domain:
                var_to_values[unassigned_var_index] = value
                if (not cons.check(var_to_values)):
                    # no solution to constraint where this unassigned_var = value
                    unassigned_var.prune_value(value)
                    pruned_values.append((unassigned_var, value))

                    if(unassigned_var.cur_domain_size() == 0):
                        return False, pruned_values # we have wiped out domain of unassigned var, solution in the current state no longer possible
        
    return True, pruned_values


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    gac_queue = []
    pruned_values = []
    d = {} # hash table to check whether or not a constraint is in the queue currently
    all_cons = csp.get_all_cons() if newVar == None else csp.get_cons_with_var(newVar)
    
    gac_queue = all_cons # intial state of the queue
    for c in gac_queue:
        d.setdefault(c, True) #intialize the hash table, each cons is in the queue
     
    while (len(gac_queue) > 0):
        curr_cons = gac_queue.pop(0)
        d[curr_cons] = False # Constraint is not in the queue  anymore

        for var in curr_cons.get_scope():
            if(not var.is_assigned()):
                # We can only prune values in domain of unassigned variable
                var_curr_domain = var.cur_domain()
                for value in var_curr_domain:
                    if(not curr_cons.has_support(var, value)):
                        #Prune the value from the domain of var
                        var.prune_value(value)
                        pruned_values.append((var, value))

                        if(var.cur_domain_size() == 0):
                            # Reach dead end
                            return False, pruned_values
                        
                        # We may have to push all constraints that we indirectly affected back 
                        # Into the queue. Note, if the constraint is already in queue we don't push it again
                        for cons in csp.get_cons_with_var(var):
                            if not d.get(cons, False):
                                d[cons] = True
                                gac_queue.append(cons)


    return True, pruned_values            


def ord_mrv(csp):
    ''' Return variable according to the Minimum Remaining Values Heuristic '''
    mrv = None
    unassigned_vars = csp.get_all_unasgn_vars()
    for var in unassigned_vars:
        if mrv == None:
            mrv  = var
        
        else:
            if(var.cur_domain_size() < mrv.cur_domain_size()):
                mrv = var
    return mrv           

