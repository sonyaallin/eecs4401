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

    if newVar:
        #forward check all constraints with one uninstanciated variable 
        tpruned = []
        v = newVar
        cons_w_var = [cons for cons in csp.get_cons_with_var(v) if cons.get_n_unasgn()==1]
        for con in cons_w_var:              # for each constraint...
            x = con.get_unasgn_vars()[0]    # get unassigned variable
            success, pruned = FC_helper(con, x, v)   # call FC helper
            tpruned += pruned
            if not success:                 # if we didnt have a DWO, then return True with prunes
                return False, tpruned
        return True, tpruned
    else: # preprocessing step. Assume nothing is assigned
        tpruned = []
        cons_w_one = [cons for cons in csp.get_all_cons() if cons.get_n_unasgn()==1]
        for con in cons_w_one:              # for each constraint...
            x = con.get_scope()[0]          # get unassigned variable
            print(x)
            success, pruned = FC_helper(con, None, x)   # call FC helper
            tpruned += pruned
            if not success:                     # if we didnt have a DWO, then return True with prunes
                return False, tpruned
        return True, tpruned


def FC_helper(constraint, set_var, rem_var):
    ''' Given a constraint and the remaining variable, attempt value assignments
    and if they falsify the constraint, prune value from variable's current domain'''
    if set_var:
        pruned_vals = []
        for val in rem_var.domain():
            if rem_var.in_cur_domain(val):
                if not constraint.check((set_var.get_assigned_value(), val)):
                    # if (V_val , X_val) is not in the sat tuple, then it needs to be pruned
                    pruned_vals.append((rem_var, val)) # add (var, value) to pruned list
                    rem_var.prune_value(val)    # prune value in variable
        if rem_var.cur_domain_size() == 0:      # if there is a DWO for the variable, return False and pruned vals
            return False, pruned_vals
        return True, pruned_vals                      # else, return True and the pruned values
    else:
        pruned_vals = []
        for val in rem_var.domain():
            if rem_var.in_cur_domain(val):
                if not constraint.check((val,)):
                    # if (X_val,) is not in the sat tuple, then it needs to be pruned
                    pruned_vals.append((rem_var, val)) # add (var, value) to pruned list
                    rem_var.prune_value(val)    # prune value in variable
        if rem_var.cur_domain_size() == 0:      # if there is a DWO for the variable, return False and pruned vals
            return False, pruned_vals
        return True, pruned_vals                      # else, return True and the pruned values


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    gac_queue = []
    tpruned = []
    if newVar:
        # add constraints that contain newVar in queue
        gac_queue = csp.get_cons_with_var(newVar)
    else:
        # add all constraints to queue
        gac_queue = csp.get_all_cons().copy()   
    while gac_queue != []:                  # while the queue is not empty
        con = gac_queue.pop(0)              # pop from front of queue
        uvars = con.get_unasgn_vars()       # get unassigned variable
        for var in uvars:                   # for each variable in the non assigned variables
            pruned_vals = []
            for val in var.domain():        # for each value in it's domain
                if not con.has_support(var, val):   # if there is no support for this value, prune it
                    pruned_vals.append((var, val))  # add (var, value) to pruned list
                    var.prune_value(val)            # prune value in variable
                    # update queue with constraints affected 
                    for cons in csp.get_cons_with_var(var): 
                        if cons not in gac_queue:
                            gac_queue.append(cons)
            tpruned += pruned_vals
            if var.cur_domain_size() == 0:  # if we have a DWO, we have no solution
                return False, tpruned
    return True, tpruned


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    curr_low = -1
    for var in csp.get_all_unasgn_vars():
        if curr_low == -1:
            curr_low = var
        elif var.cur_domain_size() < curr_low.cur_domain_size():
            curr_low = var
    return curr_low
    
