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
    # track tuples which have been pruned
    pruned = []

    # Get the constraints for the CSP
    if newVar != None:
        constraints = csp.get_cons_with_var(newVar)
    else:
        constraints = csp.get_all_cons()

    for con in constraints:
        # See if we can use Forward Checking
        if con.get_n_unasgn() == 1:

            sol = []
            var_i = 0
            var = None
            scope = con.get_scope()
            
            # A more efficient solution over simply calling has_support() :)
            for i in range(len(scope)):

                # create new list whose unnasigned variable is tracked in the list
                if scope[i].is_assigned():
                    sol.append(scope[i].get_assigned_value())
                else:
                    # this is the unnasigned variable who we will track
                    var_i = i
                    var = scope[i]
                    sol.append(0)
            
            # Check which values in the variables domain don't satisfy
            for val in var.cur_domain():
                sol[var_i] = val
                if not con.check(sol):
                    var.prune_value(val)
                    pruned.append((var, val))

            ### Slower code for same purpose ###
            # # This is the only unassigned variable
            # var = con.get_unasgn_vars()[0]
            # # Find values which will break constraint and prune
            # for val in var.cur_domain():
            #     if not con.has_support(var, val):
            #         var.prune_value(val)
            #         pruned.append((var, val))

            # See if domain is empty - DWO
            if var.cur_domain_size() == 0:
                return False, pruned

    return True, pruned


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    pruned = []
    supports = []
    support_found = False

    # Get the constraints for the CSP
    if newVar != None:
        constraints = csp.get_cons_with_var(newVar)
    else:
        constraints = csp.get_all_cons()

    # initial population of gacqueue
    gacqueue = constraints.copy()

    # solve constraints until all constriants are satisfied
    while gacqueue != []:
        # retrieve constraint from queue
        con = gacqueue.pop(0)
        scope = con.get_scope()
        # iterate each member of con
        for var in scope:
            for val in var.cur_domain():
                supports.append(val)

                # Begin building A - supports of other vars
                for varu in scope:
                    if varu == var:
                        continue
                    for valu in varu.cur_domain():

                        if con.has_support(varu, valu):
                            supports.append(valu)
                            support_found = True
                            break
                    
                    # Varu has no values for con, so A cannot exist
                    if not support_found:
                        var.prune_value(val)

                        pruned.append((var, val))

                        # DWO has occured
                        if not var.cur_domain() or var.cur_domain()[0] == var.get_assigned_value():
                            gacqueue = []
                            return False, pruned
                        else:
                            # Requeue constraints with var in them (not "con")
                            temp = csp.get_cons_with_var(var)
                            for t in temp:
                                if t not in gacqueue:
                                    gacqueue.append(t)

                    support_found = False

    return True, pruned


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    smallest_dom = float('inf')
    smallest_var = None

    # find the unnassigned variable with smallest domain size
    for var in csp.get_all_unasgn_vars():
        size = var.cur_domain_size()
        
        if size < smallest_dom:
            smallest_var = var
            smallest_dom = size

            # force variable to return if size 1 (smallest possible domain)
            if size == 1:
                return var

    return smallest_var
