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
    pruned_assignments = []
    if newVar is None:
        cons = csp.get_all_cons()
    else:
        cons = csp.get_cons_with_var(newVar)

    for c in cons:
        unassigned_vars = c.get_unasgn_vars()
        if len(unassigned_vars) == 1:
            unassigned_variable = unassigned_vars[0]
            var_domain = unassigned_variable.cur_domain()
            all_variables = c.get_scope()

            for value in var_domain:
                vals = []
                # assign the unassigned variable with a value in its domain
                for var in all_variables:
                    # the current assigned value for this variable
                    curr = var.get_assigned_value()
                    # add them all into a list in order to check later
                    if curr:
                        vals.append(curr)
                    else:
                        vals.append(value)

                if c.check(vals) is False:
                    unassigned_variable.prune_value(value)
                    # we checked this pair and know it doesn't work so we add it
                    # to a list of pruned var,value tuples
                    pruned_assignments.append((unassigned_variable, value))

            if unassigned_variable.cur_domain_size() == 0:
                # domain wipe out check
                return False, pruned_assignments

    return True, pruned_assignments


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    pruned_assignments = []
    gac_queue = []
    if newVar is None:
        cons = csp.get_all_cons()
        for c in cons:
            gac_queue.append(c)
    else:
        cons = csp.get_cons_with_var(newVar)
        for c in cons:
            gac_queue.append(c)

    while gac_queue:
        # extract from GACQueue
        c = gac_queue.pop()
        # for V each member of scope(C)
        all_variables = c.get_scope()
        for variable in all_variables:
            for d in variable.cur_domain():
                # Find an assignment for all other variables in scope
                if not c.has_support(variable, d):
                    # If not found remove d from domain of variable
                    if variable.in_cur_domain(d):
                        variable.prune_value(d)
                        pair = (variable, d)
                        pruned_assignments.append(pair)

                    # DWO condition for variable
                    if variable.cur_domain_size() == 0:
                        # empty GACqueue and return DWO
                        gac_queue = []
                        return False, pruned_assignments
                    else:
                        # push all constraints in C such that variable in its scope
                        for new_cons in csp.get_cons_with_var(variable):
                            if new_cons not in gac_queue:
                                gac_queue.append(new_cons)
    return True, pruned_assignments


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    global output
    minimum = float("inf")
    all_variables = csp.get_all_unasgn_vars()
    for var in all_variables:
        if var.cur_domain_size() < minimum:
            minimum = var.cur_domain_size()
            output = var
    if output:
        return output
    else:
        return None
