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

import cspbase


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
    constraints = None
    prunes = []
    # Get relevant constraints from csp
    if newVar:
        constraints = csp.get_cons_with_var(newVar)
    else:
        constraints = csp.get_all_cons()
    for cons in constraints:
        # If only 1 unassigned var
        if cons.get_n_unasgn() == 1:
            var = cons.get_unasgn_vars()[0]
            curr_dom = var.cur_domain()
            # Check each possible val, prune if condition isnt satisfied
            for val in curr_dom:
                if not cons.has_support(var, val):
                    var.prune_value(val)
                    prunes.append((var, val))
            if var.cur_domain_size() == 0:
                # Domain wipeout
                return False, prunes
    return True, prunes


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    constraints = None
    prunes = []
    if newVar:
        constraints = csp.get_cons_with_var(newVar).copy()
    else:
        constraints = csp.get_all_cons().copy()
    # Dequeue from the beginning, Enqueue to the end
    gac_queue = constraints.copy()
    while gac_queue:
        # Pop current constraint
        curr_cons = gac_queue.pop(0)
        scope = curr_cons.get_scope()
        for var in scope:
            if var.cur_domain_size() == 0:
                # Domain wipeout
                return False, prunes
            domain = var.cur_domain()
            for val in domain:
                # If current value does not satisfy, prune
                if not curr_cons.has_support(var, val):
                    var.prune_value(val)
                    prunes.append((var, val))
                    # Enqueue all constraints with var if not enqueued already
                    for cons in constraints:
                        if var in cons.get_scope() and cons not in gac_queue:
                            gac_queue.append(cons)
    return True, prunes

        


def ord_mrv(csp: cspbase.CSP):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    csp_vars = csp.get_all_unasgn_vars()
    if not csp_vars:
        return None
    smallest_domain = csp_vars[0]
    for var in csp_vars:
        if var.cur_domain_size() < smallest_domain.cur_domain_size():
            smallest_domain = var
    return smallest_domain

