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

import numpy as np


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
    prunings = []
    for c in csp.get_all_cons():
        if newVar is not None and newVar not in c.get_scope():
            continue
        elif c.get_n_unasgn() != 1:
            continue
        else:
            # obtain assigned values for all variables in the scope
            lst = np.array([v.get_assigned_value() for v in c.get_scope()])

            # obtain an unassigned variable
            # check each value in the current domain
            var = c.get_unasgn_vars()[0]
            for x in var.cur_domain():
                # replace None with x
                vals = np.where(lst == None, x, lst)
                # pruning if lst does not satisfy the constraint
                if not c.check(vals):
                    var.prune_value(x)
                    prunings.append((var, x))
            # domain wipe-out
            if not var.cur_domain():
                return False, prunings
    return True, prunings


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # initialize queue
    if newVar is None:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)
    queue = [i for i in range(len(constraints))]

    prunings = []
    while queue:
        # perform GAC on a constraint popped out from the queue
        pruned_vars = []
        c = constraints[queue.pop(0)]
        for var in c.get_scope():
            for val in var.cur_domain():
                if not c.has_support(var, val):
                    var.prune_value(val)
                    prunings.append((var, val))
                    pruned_vars.append(var)
            # domain wipe-out
            if not var.cur_domain():
                return False, prunings

        # add constraints back into the queue
        for var in pruned_vars:
            for i, c in enumerate(constraints):
                if var in c.get_scope() and i not in queue:
                    queue.append(i)
    return True, prunings


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    min_v = None
    min_v_size = 1e6
    for v in csp.get_all_unasgn_vars():
        v_size = v.cur_domain_size()
        if v_size < min_v_size:
            min_v_size = v_size
            min_v = v
    return min_v
