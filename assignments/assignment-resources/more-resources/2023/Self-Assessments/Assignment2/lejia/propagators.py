# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete problem solution.

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

### Helper Functions ###
def get_constraints(csp, newVar=None):
    """ Helper function for getting constraints, used in FC and GAC.
    If newVar=None, return list of all constraints,
    otherwise, return list of constraints with var
    """
    if newVar is None:
        return csp.get_all_cons()

    return csp.get_cons_with_var(newVar)

def FC_check(cons, var):
    """ FC function from slide 49 week 4
    This function should return if constraint was satisfied (true)
    or if DWO occurred (false) and pruned values as a list of key-value tuples.
    """
    pruned_vals = []

    for member in var.cur_domain():
        # assign member to var which is referenced in Constraint scope
        # attribute.
        var.assign(member)

        # Extract assigned value of each variable specific to this
        # constraint
        assigned_vals = [var.get_assigned_value() for var in cons.get_scope()]

        if not cons.check(assigned_vals):
            # current var assignment falsifies our constraint so we prune
            var.prune_value(member)
            pruned_vals.append((var, member))

        # remember to unassign member after checking with scope
        var.unassign()

    # If curr domain is empty, DWO has occurred
    if var.cur_domain_size() == 0:
        return False, pruned_vals

    return True, pruned_vals

def GAC_enforce(csp, cons_q):
    """ GAC_enforce function from slide 12 week 5
    Check all constraints to increase pruning.
    """
    pruned_vals = []

    while len(cons_q) > 0:
        cons = cons_q.popleft()

        for var in cons.get_scope():
            for member in var.cur_domain():
                if not cons.has_support(var, member):
                    # no supporting tuple so prune from curr domain
                    var.prune_value(member)
                    pruned_vals.append((var, member))

                    if var.cur_domain_size() == 0:
                        # DWO occurred, empty the queue
                        cons_q = deque([])
                        return False, pruned_vals
                    else:
                        # enqueue all constraints c s.t. var in scope(c)
                        # and c not in cons_q already
                        for c in csp.get_cons_with_var(var):
                            if c not in cons_q:
                                cons_q.append(c)

    return True, pruned_vals

### End of Helper Functions ###

# When newVar is None, we are just performing basic preprocessing
def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var,
       only check constraints containing newVar'''
    # IMPLEMENT
    pruned_vals = []
    constraints = get_constraints(csp, newVar)
    satisfied = True

    # Iterate over all constraints and check if each one has
    # exactly ONE uninstantiated variable in their scope
    for cons in constraints:
        # this condition applies for both newVar=None and newVar=var
        if cons.get_n_unasgn() != 1:
            continue

        unassigned_var = cons.get_unasgn_vars()[0]

        # run FC_check on the unassigned variable with this constraint
        satisfied, cons_pruned_vals = FC_check(cons, unassigned_var)
        pruned_vals += cons_pruned_vals

        # Constraint not satisfied, no need to continue checking
        if not satisfied:
            break

    # Propogator returns tuple[bool, list[tuple]]
    # bool conveys whether constraints were satisfied
    # tuple in list consists of (Variable, value)
    return satisfied, pruned_vals

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    # optimize dequeue and enqueue using double ended queue
    # we will use front of deque as front of queue
    cons_q = deque(get_constraints(csp, newVar))

    satisfied, pruned_vals = GAC_enforce(csp, cons_q)

    return satisfied, pruned_vals

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    # a variable ordering heuristic that chooses the next variable to be assigned
    # ccording to the Minimum Remaining Values (MRV) heuristic. The ord_mrv method
    # returns the variable with the most constrained current domain (i.e., the
    # variable with the fewest legal values).

    variables = csp.get_all_unasgn_vars()

    if len(variables) == 0:
        return None

    min_var = variables[0]

    for var in variables:
        if var.cur_domain_size() < min_var.cur_domain_size():
            min_var = var

    return min_var
