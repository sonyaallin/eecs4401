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
    pruned_pairs = []
    constraints = []
    DWOoccured = False

    if newVar == None:
        constraints = csp.get_all_cons()
        for constraint in constraints:
            if constraint.get_n_unasgn() == 1:
                unassigned_var = constraint.get_scope()[0]
                DWOoccured, pruned_pairs = first_check_FC(constraint, unassigned_var, pruned_pairs)
                if DWOoccured:
                    return False, pruned_pairs
        #REST
    elif newVar != None:
        #print("newVar: "+str(newVar))
        constraints = csp.get_cons_with_var(newVar)
        for constraint in constraints:
            if constraint.get_n_unasgn() == 1:
                #unassigned_var = constraint.get_unasgn_vars()[0]
                DWOoccured, pruned_pairs = check_FC(constraint, pruned_pairs)
                if DWOoccured:
                    return False, pruned_pairs
    return True, pruned_pairs

def first_check_FC(constraint, unassigned_var, pruned_pairs):
    for value in unassigned_var.cur_domain():
        if constraint.check([value]) == False:
            unassigned_var.prune_value(value)
            pruned_pairs.append((unassigned_var, value))
            if unassigned_var.cur_domain_size() == 0:
                return True, pruned_pairs
    return False, pruned_pairs

def check_FC(constraint, pruned_pairs):
    scope = constraint.get_scope()
    scope_len = len(scope)
    #unassigned_index = scope.index(unassigned_var)
    values = []
    unassigned_var = None
    unassigned_index = None

    for i in range(0, scope_len):
        if not scope[i].is_assigned():
            values.append(None)
            unassigned_var = scope[i]
            unassigned_index = i
        else:
            values.append(scope[i].get_assigned_value())
    
    for value in unassigned_var.cur_domain():
        values[unassigned_index] = value
        if constraint.check(values) == False:
            unassigned_var.prune_value(value)
            pruned_pairs.append((unassigned_var, value))
    if unassigned_var.cur_domain_size() == 0:
        return True, pruned_pairs
    return False, pruned_pairs


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    pruned_pairs = []
    GACqueue = []
    DWOoccured = False

    if newVar == None:
        GACqueue = csp.get_all_cons()
        DWOoccured = enforce_GAC(csp, GACqueue, pruned_pairs)
        if DWOoccured:
            return False, pruned_pairs
    elif newVar != None:
        GACqueue = csp.get_cons_with_var(newVar)
        DWOoccured = enforce_GAC(csp, GACqueue, pruned_pairs)
        if DWOoccured:
            return False, pruned_pairs
    return True, pruned_pairs

def enforce_GAC(csp, GACqueue, pruned_pairs):
    
    
    while GACqueue != []:
        curr_constraint = GACqueue.pop(0)
        curr_scope = curr_constraint.get_scope()
        
        for var in curr_scope:
            pruned = False
            if not var.is_assigned():
                for value in var.cur_domain():
                    if not curr_constraint.has_support(var, value):
                        var.prune_value(value)
                        pruned_pairs.append((var, value))
                        pruned = True
                        if var.cur_domain_size == 0:
                            GACqueue.clear()
                            return True
                if pruned:
                    for constraint in csp.get_cons_with_var(var):
                        if constraint != curr_constraint and constraint not in GACqueue:
                            GACqueue.append(constraint)
    return False




def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    vars = csp.get_all_vars()
    smallest_domain = None
    smallest_domain_var = None
    for var in vars:
        if not var.is_assigned():
            dom_size = var.cur_domain_size()
            if smallest_domain == None or dom_size < smallest_domain:
                smallest_domain = dom_size
                smallest_domain_var = var
    return smallest_domain_var