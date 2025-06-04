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
    lst_constraints = []
    lst_pruned = []

    if not newVar:
        lst_constraints = csp.get_all_cons()
    else:
        lst_constraints = csp.get_cons_with_var(newVar)

    for c in lst_constraints:
        if c.get_n_unasgn() == 1:  # if there's only 1 unassigned variable
            curr_var = c.get_unasgn_vars()[0]
            # Go through each value in the domain to check for values to prune based on it
            for val in curr_var.cur_domain():
                if not c.has_support(curr_var, val):
                    var_val_pair = (curr_var, val)

                    if var_val_pair not in lst_pruned:
                        # Put curr prune on backburner in case restoration required
                        lst_pruned.append(var_val_pair)
                        curr_var.prune_value(val)

            # If domain wipeout has occured, return False
            if curr_var.cur_domain_size() == 0:
                return False, lst_pruned
    return True, lst_pruned


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    gac_queue = []
    lst_constraints = []
    lst_pruned = []

    if not newVar:
        lst_constraints = csp.get_all_cons()
    else:
        lst_constraints = csp.get_cons_with_var(newVar)

    # Populate the GAC Queue with the constraints
    for c in lst_constraints:
        gac_queue.append(c)

    while len(gac_queue) != 0:
        con = gac_queue.pop(0)

        # Go through all variables in scope instead of only 1 unassigned variable
        for var in con.get_scope():
            
            # Go through each value in the domain to check for values to prune based on it
            for val in var.cur_domain():

                if not con.has_support(var, val):
                    var_val_pair = (var, val)

                    if var_val_pair not in lst_pruned:
                        lst_pruned.append(var_val_pair)

                        # Put curr prune on backburner in case restoration required
                        var.prune_value(val)

                    # If domain wipeout has occured, return False
                    if var.cur_domain_size() == 0:
                        gac_queue.clear()
                        return False, lst_pruned

                    # Add all constraints from this var (which got its domain pruned) to the GAC Queue
                    else:
                        for constraint in csp.get_cons_with_var(var):
                            if constraint not in gac_queue:
                                gac_queue.append(constraint)
    return True, lst_pruned


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    min_rem_var = None
    dom_size = 0

    for var in csp.get_all_unasgn_vars():
        if dom_size <= 0:
            min_rem_var = var
            dom_size = var.cur_domain_size()

        # If there are less values remaining in the curr var's domain, then that is the MRV var
        elif var.cur_domain_size() <= dom_size:
            min_rem_var = var
            dom_size = var.cur_domain_size()

    # Var is going to be assigned so remove it
    csp.get_all_unasgn_vars().remove(min_rem_var)
    return min_rem_var
