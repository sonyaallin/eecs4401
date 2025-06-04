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

    # Get the constraints with respect to newVar
    if newVar is None:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)

    # Get unary constraints
    unary = []
    for cons in constraints:
        if cons.get_n_unasgn() == 1:
            unary.append(cons)

    pruned = []
    for cons in unary:
        unassigned = cons.get_unasgn_vars()[0]
        cur_domain = unassigned.cur_domain()

        # Retrieve other variable assignment of the constraint and put them in order
        vals = []
        cons_scope = cons.get_scope()
        index = -1
        for i in range(len(cons_scope)):
            if cons_scope[i].assignedValue is not None:
                vals.append(cons_scope[i].assignedValue)
            else:
                vals.append(0)
                index = i

        # Prune falsifiable values

        for val in cur_domain:
            vals[index] = val
            if not cons.check(vals):
                unassigned.prune_value(val)
                pruned.append((unassigned, val))
        
        # Domain Wipe Out
        if unassigned.cur_domain() == []:
            return False, pruned
    return True, pruned
            

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT

    # Get the constraints with respect to newVar
    if newVar is None:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)
    
    pruned = []

    while constraints != []:
        # Extract first constrinat from the queue
        cons = constraints[0]
        constraints = constraints[1:]

        # Check GAC for all variables
        for var in cons.get_scope():
            prune = False
            for val in var.cur_domain():
                if not cons.has_support(var, val):
                    var.prune_value(val)
                    prune = True
                    pruned.append((var, val))
            if var.cur_domain() == []:
                return False, pruned
            elif prune:
                newCons = csp.get_cons_with_var(var)
                for newCon in newCons:
                    if newCon not in constraints and newCon != cons:
                        constraints.append(newCon)
    return True, pruned

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    unassigned = csp.get_all_unasgn_vars()
    min_rem = None
    selected = None
    for var in unassigned:
        remaining = var.cur_domain_size()
        if min_rem is None:
            min_rem = remaining
            selected = var
        elif remaining < min_rem:
            min_rem = remaining
            selected = var
    return selected



