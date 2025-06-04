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
    # IMPLEMENT


    if not newVar:
        # first we get all cons and only get the ones with one unassigned var
        list_cons_to_check = list(filter((lambda c: c.get_n_unasgn() == 1),csp.get_all_cons()))
    else:
        # o.w. we only get the constraints that relates to Var and one unassigned var
        list_cons_to_check = list(filter((lambda c: c.get_n_unasgn() == 1),csp.get_cons_with_var(newVar)))
        #print(str("checking ") + str(newVar) + " with val " + str(newVar.get_assigned_value()) + " ... " + str(len(list_cons_to_check)) + " constraints")
    # Check each cons
    pruned = []
    for c in list_cons_to_check:
        unasgnd_var = c.get_unasgn_vars()[0]
        DWO, p = FCCheck(c,unasgnd_var)
        pruned = pruned + p # concatentate new pruned list with old one
        if DWO is True: #Domain wipe out!
            #print(str(unasgnd_var) + " got a DWO!")
            return False, pruned
    return True, pruned
 


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    if not newVar:
        gac_enforce_list = csp.get_all_cons()
    else:
        gac_enforce_list = csp.get_cons_with_var(newVar)
    return gac_enforce(csp,gac_enforce_list)

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    all_unasgnd_vars = csp.get_all_unasgn_vars()
    # we sort list of all unassigned vars by the current domain size (ascending order)
    all_unasgnd_vars.sort(key=(lambda v: v.cur_domain_size()),reverse=False)
    return all_unasgnd_vars[0]


# Helper functions

def FCCheck(constraint,unasgnd_var):
    # prereq: constraint only has one unassigned variable!
    # outputs: DWO, pruned
    cur_domain = unasgnd_var.cur_domain()
    # we assume that there is only one None value because of prereq
    scopeVals = list(map((lambda v: v.get_assigned_value()),constraint.get_scope()))
    indexNone = scopeVals.index(None) # Find where None is in scopeVals.
    pruned = []
    # Now we will test all values of x in current domain and check if they
    # satisfy the constraint. Prune if they do not.
    for x in cur_domain:
        scopeVals[indexNone] = x
        # Check if scopeVals satisfy constraint or not
        if constraint.check(scopeVals) is False:
            unasgnd_var.prune_value(x)
            pruned.append((unasgnd_var,x))

    if unasgnd_var.cur_domain_size() == 0:
        return True, pruned
    else:
        return False, pruned


def gac_enforce(csp,gac_queue):
    all_pruned = []
    while len(gac_queue) > 0:
        c = gac_queue.pop(0)
        cvars = c.get_scope()
        for var in cvars:
            # ignore assigned variables
            if var.is_assigned():
                continue
            # get the current domain of var and its index
            cur_domain = var.cur_domain()
            index = cvars.index(var)
            pruned = False
            for d in cur_domain:
                test_tuple = list(map((lambda v: v.get_assigned_value()),cvars))
                test_tuple[index] = d
                result = gac_satisfiable(c,test_tuple,cvars)
                if result is False:
                    all_pruned.append((var,d))
                    pruned = True
                    var.prune_value(d) 
            
            if var.cur_domain_size() == 0:
                return False, all_pruned
            
            if pruned:
                # add all constraints with var back to the queue
                all_var_cons = csp.get_cons_with_var(var)
                for c2 in all_var_cons:
                    if c2 not in gac_queue:
                        gac_queue.append(c2)

    return True, all_pruned


def gac_satisfiable(constraint, test_tuple, cvars):
    # Accepts a constraint, a tuple of values (includes Nones) and a list of variables
    # Outputs True if there exists a valid tuple that satisfies the contraint
    for i in range(len(test_tuple)):
        # Ignore if it is not None
        if test_tuple[i] is not None:
            continue
        # We test all values in cvars[i]
        chosen_var = cvars[i]
        cur_domain = chosen_var.cur_domain()
        for d in cur_domain:
            test_tuple[i] = d
            if gac_satisfiable(constraint, test_tuple, cvars):
                return True
        # If we get here then no value for cvars[i] satifies constraint, so it is not GAC
        test_tuple[i] = None
        return False

    # If we get here then no value in test_tuple is None, so it is a tuple we should test
    return constraint.check(test_tuple)