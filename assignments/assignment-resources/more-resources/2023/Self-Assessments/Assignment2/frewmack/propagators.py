from collections import deque

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
    # use set to avoid duplicate prunes
    pruned_vals = set()
    if not newVar:
        # Check all unary constraints
        unary_cons = filter(lambda con: len(con.get_scope()) == 1, csp.get_all_cons())
        for unary_con in unary_cons:
            constrained_var = unary_con.get_scope()[0]
            for val in constrained_var.cur_domain():
                if not unary_con.check([val]):
                    constrained_var.prune_value(val)
                    pruned_vals.add((constrained_var, val))
            if constrained_var.cur_domain_size() == 0:
                return False, list(pruned_vals)

    else:
        # Check all constraints with 1 uninstantiated variable that involve newVar
        for c in filter(lambda con: con.get_n_unasgn() == 1, csp.get_cons_with_var(newVar)):
            unasgn_index = None
            template_vals = []
            vars = c.get_scope()
            # Generate a template list for c.check, where all values are present 
            # except for the unassigned one, which we iterate on for all values in its domain
            for i in range(len(vars)):
                if vars[i].is_assigned():
                    template_vals.append(vars[i].get_assigned_value())
                else:
                    template_vals.append(None)
                    unasgn_index = i
            try:
                constrained_var = vars[unasgn_index]
            except TypeError:  # unasgn_index = None
                # shouldn't ever happen, but just in case
                raise Exception(f"Constraint {c.name} has no unassigned values!")
            for val in constrained_var.cur_domain():
                try_vals = template_vals.copy()
                try_vals[unasgn_index] = val
                if not c.check(try_vals):
                    constrained_var.prune_value(val)
                    pruned_vals.add((constrained_var, val))
            if constrained_var.cur_domain_size() == 0:
                return False, list(pruned_vals)

    return True, list(pruned_vals)


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    GAC_queue = deque()
    pruned_vars = set()
    if not newVar:
        # Check every constraint
        for c in csp.get_all_cons():
            GAC_queue.appendleft(c)
    else:
        # Check constraints related to newVar
        for c in csp.get_cons_with_var(newVar):
            GAC_queue.appendleft(c)

    while len(GAC_queue) > 0:
        c = GAC_queue.pop()
        for var in c.get_scope():
            for val in var.cur_domain():
                if not c.has_support(var, val):
                    var.prune_value(val)
                    pruned_vars.add((var, val))
                    if var.cur_domain_size() == 0:
                        return False, list(pruned_vars)
                    else:
                        # Push constraints that include this variable that aren't in the queue already
                        for temp_c in csp.get_cons_with_var(var):
                            if temp_c not in GAC_queue and temp_c != c:
                                GAC_queue.appendleft(temp_c)

    return True, list(pruned_vars)


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    smallest_dom_size = None
    smallest_var = None
    for var in csp.get_all_unasgn_vars():
        temp_dom_size = var.cur_domain_size()
        if smallest_dom_size is None or 0 < temp_dom_size < smallest_dom_size:
            smallest_dom_size = temp_dom_size
            smallest_var = var
    return smallest_var