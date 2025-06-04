import math
from collections import deque

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

def create_assignment(con, unasgn_var, val):
    """Returns a list of values, one for each variable in the given
    constraint's scope. Assumes that all variables except the given one has
    been assigned a value.
    """
    vals = []

    for var in con.get_scope():
        if var is unasgn_var:
            vals.append(val)  # New assignment
        else:
            vals.append(var.get_assigned_value())  # Previous assignments

    return vals

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var, 
       only check constraints containing newVar'''
    
    if newVar is not None:
        cons = csp.get_cons_with_var(newVar)
    else:
        cons = csp.get_all_cons()

    # Get constraints with only one uninstantiated variable
    cons_with_one_var = []
    for con in cons:
        if con.get_n_unasgn() == 1:
            cons_with_one_var.append(con)

    prunings = []

    for con in cons_with_one_var:
        var = con.get_unasgn_vars()[0]
        for val in var.cur_domain():
            # List of values, one for each variable in the constraint's scope
            vals = create_assignment(con, var, val)
            if not con.check(vals):
                var.prune_value(val)
                prunings.append((var, val))
        
        if var.cur_domain_size() == 0:
            return False, prunings
    
    return True, prunings

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    if newVar is not None:
        gac_queue = deque(csp.get_cons_with_var(newVar))
    else:
        gac_queue = deque(csp.get_all_cons())

    prunings = []

    while gac_queue:
        con = gac_queue.popleft()
        for var in con.get_scope():
            for val in var.cur_domain():
                # Check if the new value does not satisfy the constraint
                if not con.has_support(var, val):
                    var.prune_value(val)
                    prunings.append((var, val))

                    if var.cur_domain_size() == 0:
                        return False, prunings
                    else:
                        # Push affected constraints into the queue, if they're not already in it
                        for affected_con in csp.get_cons_with_var(var):
                            if (affected_con is not con) and (affected_con not in gac_queue):
                                gac_queue.append(affected_con)

    return True, prunings

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    next_var = None
    mrv = math.inf

    # Find the variable with the smallest curdom
    for var in csp.get_all_unasgn_vars():
        curdom_size = var.cur_domain_size()
        if curdom_size < mrv:
            next_var = var
            mrv = curdom_size

    return next_var
