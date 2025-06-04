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
    dwo = False
    prunings = []
    # get constraints depending on value of newVar
    if newVar:
        # newVar is not None, so we get all constraints that contain variable newVar
        all_cons = csp.get_cons_with_var(newVar)
    else:
        # newVar is None, so we get all constraints for preprocessing
        all_cons = csp.get_all_cons()
        
    # loop through our list of constraints for forward checking
    for cons in all_cons:
        # if constraint has one unassigned variable, we perform forward checking
        if cons.get_n_unasgn() == 1:
            # get unassigned variable
            var = (cons.get_unasgn_vars())[0]

            # perform forward checking on this constraint with its unassigned variable
            dwo, new_prunings = FCCheck(cons, var)

            # add new prunings to list of all prunings
            prunings += new_prunings

            # return false if DWO occured on this constraint
            if dwo:
                return False, prunings
    return True, prunings

def FCCheck(cons, var):
    pruned = []
    # loop through curr domain of unassigned variable
    for val in var.cur_domain():
        # assign each value to variable to see if constraint is satisfied
        var.assign(val)

        # get assignments of all variables on constraint
        asgned_vals = []
        for x in cons.get_scope():
            asgned_vals.append(x.get_assigned_value())

        # check if these assignments satisfy the constraint
        if not cons.check(asgned_vals):
            # these assignments did not satisfy the constraint, meaning the value assigned
            # to the last unassigned variable must be pruned
            var.prune_value(val)
            pruned.append((var, val))

        # unassign the variale value so we can check the next value in the domain
        var.unassign()

    # return True if DWO occured, and return prunings regardless
    if var.cur_domain_size() == 0:
        return True, pruned
    return False, pruned

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    prunings = []
    # get GACQueue depending on value of newVar
    if newVar:
        # newVar is not None, so Queue has all constraints that contain variable newVar
        GACQueue = csp.get_cons_with_var(newVar)
    else:
        # newVar is None, so Queue has all constraints for preprocessing
        GACQueue = csp.get_all_cons()
    
    # loop until the queue is empty
    while GACQueue != []:
        # pop constraint from queue
        cons = GACQueue.pop(0)
        # loop through all variable, value pairs on this constraint
        for var in cons.get_scope():
            for val in var.cur_domain():
                # check if this pair has a satisfying set of assignments
                if not cons.has_support(var, val):
                    # prune this value from the domain of this variable if there is no assignment
                    var.prune_value(val)
                    prunings.append((var,val))

                    # return False if DWO occured
                    if var.cur_domain_size() == 0:
                        return False, prunings
                    # Otherwise, add all constraints that contain the variable that had
                    # a value pruned (if not already on the Queue)
                    else:
                        for new_cons in csp.get_cons_with_var(var):
                            if new_cons not in GACQueue:
                                GACQueue.append(new_cons)
    return True, prunings

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # get all unassigned variables 
    vars = csp.get_all_unasgn_vars()
    most_contrained = None
    # get variable with smallest curr domain size(least number of possible values)
    for var in vars:
        if not most_contrained:
            most_contrained = var
        elif var.cur_domain_size() < most_contrained.cur_domain_size():
            most_contrained = var
    return most_contrained

