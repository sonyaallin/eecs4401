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
    
    constraints_to_check = None
    
    if newVar == None:
        constraints_to_check = csp.get_all_cons()
    else:
        constraints_to_check = csp.get_cons_with_var(newVar)
    
    pruned_values = list()
    
    for con in constraints_to_check:
        if con.get_n_unasgn() != 1:
            continue
        else:
            for v in (con.get_unasgn_vars()[0]).cur_domain():
                tuple_to_check = list()
                for var in con.get_scope():
                    if var.is_assigned():
                        tuple_to_check.append(var.get_assigned_value())
                    elif var == con.get_unasgn_vars()[0]:
                         tuple_to_check.append(v)
                tuple_to_check = tuple(tuple_to_check)
                if not con.check(tuple_to_check):
                    con.get_unasgn_vars()[0].prune_value(v)
                    pruned_values.append((con.get_unasgn_vars()[0],v))                    
            if (con.get_unasgn_vars()[0]).domain_size() == 0:
                return False, pruned_values
    return True, pruned_values


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    
    gac_queue = []
    pruned_values = list()
    
    if newVar == None:
        gac_queue = csp.get_all_cons()
    else:
        gac_queue = csp.get_cons_with_var(newVar)
        
    while len(gac_queue) != 0:
        con = gac_queue.pop(0)
        for var in con.get_scope():
            for v in var.cur_domain():
                if not con.has_support(var,v):
                    var.prune_value(v)
                    pruned_values.append((var,v))
                    if var.domain_size() == 0:
                        gac_queue = []
                        return False, pruned_values
                    else:
                        for con_to_add in csp.get_cons_with_var(var):
                            if con_to_add not in gac_queue:
                                gac_queue.append(con_to_add)
    
    return True, pruned_values


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    
    min_variable = None
    min_value = float('inf')
    
    
    for variable in csp.get_all_unasgn_vars():
        if variable.domain_size() < min_value:
            min_variable = variable
            min_value = variable.domain_size()
    
    return min_variable
