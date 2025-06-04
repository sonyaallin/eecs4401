from queue import Queue

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
    var_value_lst = []
    # checking if newVar is None
    if newVar is None:
        # look for constraints whose scope contains only one variable
        for constraint in csp.get_all_cons():
            if constraint.get_n_unasgn() == 1:
                # getting variable that has no assigned value
                variable = constraint.get_unasgn_vars()[0]
                # I think I need to test values for the unassigned variable to prune the ones that do  not work
                for value in variable.cur_domain():
                    # value = variable.get_assigned_value()
                    var_value = (variable, value)

                    # checking if value does not satisfy constraint and value has not been pruned already
                    # i need to create a tuple with the assigned variables and this new attempt to assign
                    scope = constraint.get_scope()
                    vals = [] # list of values, one for each variable
                    for var in scope:
                        if var.is_assigned():
                            vals.append(var.get_assigned_value())
                        else:
                            vals.append(value)
                    if not constraint.check(vals) and (variable.in_cur_domain(value)):
                        var_value_lst.append(var_value)
                        variable.prune_value(value)
                    # checking if domain wipe out occurred
                    if variable.cur_domain() == []:
                        return False, var_value_lst
        return True, var_value_lst
    # newVar is not None
    else:
        final_result = (True, [])
        # forward check all constraints with newVar that have one
        # unassigned variable left
        # looping through all constraints that have newVar
        for constraint in csp.get_cons_with_var(newVar):
            # checking if the size of the scope is 2, which means
            # that it has the given variable newVar and another
            # unassigned variable
            if constraint.get_n_unasgn() == 1:
                # performing forward check
                result = prop_FC(csp)
                if result[0] == False:
                    return result
                # appending the list from the result of the current constraint
                final_result[1].extend(result[1])
        return final_result


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    gac_queue = Queue()
    removed_from_queue = []
    var_value_list = []
    if newVar is None:
        # establish GAC by initializing the GAC queue with all constraints of
        # the csp
        for constraint in csp.get_all_cons():
            gac_queue.put(constraint)
    else:
        # initialize GAC queue with all constraints containing newVar
        for constraint in csp.get_cons_with_var(newVar):
            gac_queue.put(constraint)
    while not gac_queue.empty():
        constraint = gac_queue.get()
        for var in constraint.get_scope():
            for value in var.domain():
                # i might not need to assign the value to the variable
                if not constraint.has_support(var, value):
                    var.prune_value(value)
                    var_value_list.append((var, value))
                    # checking if DWO happened
                    if var.domain_size() == 0:
                        gac_queue = Queue()
                        return False, var_value_list
                    # pushing constraints that are related to pruned variable b
                    # ack into the queue
                    constraints_to_be_added = csp.get_cons_with_var(var)
                    for c in constraints_to_be_added:
                        if c in removed_from_queue:
                            removed_from_queue.remove(c)
                            gac_queue.put(c)
    return True, var_value_list


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    variables = csp.get_all_unasgn_vars()
    final_var = variables[0]
    for var in variables:
        if var.domain_size() < final_var.domain_size():
            final_var = var
    return final_var
