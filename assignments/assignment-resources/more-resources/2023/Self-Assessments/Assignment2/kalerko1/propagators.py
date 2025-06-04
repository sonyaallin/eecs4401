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


from telnetlib import GA
from cspbase import CSP, Constraint, Variable


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
    #pass
    test_vals = []
    if not newVar:
        cons = csp.get_all_cons()
    else:
        cons = csp.get_cons_with_var(newVar)
    pruned = []

    for c in cons:
        if c.get_n_unasgn() == 1:
            vals = []
            var = c.get_unasgn_vars()[0] # should be only 1
            vals = var.cur_domain() # get curr_domain since prev mght have pruned
            for val in vals:
                if not c.has_support(var,val): # check if var val pair has future support, else prune from curr_domain
                    var.prune_value(val) 
                    pruned.append((var,val))
            if var.cur_domain() == []: 
                return False, [] # var.restore_curdom() DONT KNOW WHICH ONE
    return True, pruned



def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    pruned_vals = []
    if newVar != None:
        GACQueue = csp.get_cons_with_var(newVar)
    else:
        GACQueue = csp.get_all_cons()

    while GACQueue != []:
        con = GACQueue[0]
        vars = con.get_scope()

        for var in vars:
            for val in var.cur_domain():
                #check which val in curdom works
                if not con.has_support(var,val):
                    if (var,val) not in pruned_vals:
                        var.prune_value(val)
                        pruned_vals.append((var,val))
                    #if no possible val
                    if var.cur_domain_size() == 0:
                        return False, pruned_vals
                    else:
                        #add cons with newVar to queue
                        related_cons = csp.get_cons_with_var(var)
                        for i in related_cons:
                            if i not in GACQueue:
                                GACQueue.append(i)
        GACQueue.remove(con)

    return True, pruned_vals                            


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    unassigned_vars = csp.get_all_unasgn_vars()
    if len(unassigned_vars) < 0:
        return False

    smallest_var = csp.get_all_unasgn_vars()[0]
    for var in unassigned_vars:
        if var.cur_domain_size() < smallest_var.cur_domain_size():
            smallest_var = var

    return smallest_var
