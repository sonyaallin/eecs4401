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


def FC_Check(c, X):
    pruned = []
    # go through different assignments of selected variable (will be element None in list)
    for d in X.cur_domain():
        # prune (variable:value) pair that violates constraint, continue
        # Note: we are only pruning from X's domain because (as far as we know) all
        #       other assignment are 'correct'
        if not c.has_support(X, d):
            pruned.append((X, d))
            X.prune_value(d)
            
    if not X.cur_domain():
        return False, pruned # DWO
    return True, pruned

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var, 
       only check constraints containing newVar'''
    
    pruned = [] # keep track of all pruned variable:value pairs
    
    # # check ALL cons if newVar is None, else only check constraints that contain newVar
    cons = csp.get_all_cons() if not newVar else csp.get_cons_with_var(newVar)

    # # forward check constraints that have one unassigned variable
    for c in cons:
        if c.get_n_unasgn()==1:
            X = c.get_unasgn_vars()[0] # pick the only unassigned variable

            check_next, prune_i = FC_Check(c, X)
            pruned.extend(prune_i) # add pruned values from this constraint to list of all pruned
            if not check_next:
                return False, pruned # DWO
    return True, pruned

def GAC_Enforce(csp, queue):
    # queue contains all constraints whose variables has had its domain reduced,
    # as well as at the root of the search tree, when ALL constraints are queued
    pruned = []
    while queue:
        con=queue.pop(0)
        for v in con.get_scope():
            for d in v.cur_domain():
                # prune value if the assignment has no support 
                if not con.has_support(v, d):
                    pruned.append((v, d))
                    v.prune_value(d)
                    if not v.cur_domain():
                        queue.clear()
                        return False, pruned # DWO
                    # otherwise, enqueue all constraints of v that are not already in queue
                    for c in csp.get_cons_with_var(v):
                        if c not in queue:
                            queue.append(c)
    return True, pruned

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    
    if not newVar: # initial enfore before recursive BT
        return GAC_Enforce(csp, csp.get_all_cons())

    # otherwise, prune all values in cur_domain() of newVar that do not equal newVar.get_assigned_value()
    pruned = []
    val=newVar.get_assigned_value()
    for d in newVar.cur_domain():
        if d!=val:
            newVar.prune_value(d)
            pruned.append((newVar, d))

    # queue encoded as list, pop(0) to dequeue, append to enqueue
    status, prune = GAC_Enforce(csp, csp.get_cons_with_var(newVar))
    pruned.extend(prune)
    return status, pruned


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    return min(csp.get_all_unasgn_vars(), key=lambda v : len(v.cur_domain())) # min based on length of current domain

