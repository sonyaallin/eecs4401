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

# Helper functions

def falsifies(csp, c, x, d):

    scope = c.get_scope()

    vals = []
    for v in scope:
        if v.name == x.name:
            vals.append(d)
        else:
            vals.append(v.get_assigned_value())

    return not c.check(vals)


def getFCConstraints(csp, v=None):

    constraints = []

    #print("Constraints: " + str(v))

    if v is None:
        for c in csp.get_all_cons():
            #print(c)
            if c.get_n_unasgn() == 1:
                constraints.append((c, c.get_unasgn_vars()[0]))
    else:
        for c in csp.get_cons_with_var(v):
            if c.get_n_unasgn() == 1:
                constraints.append((c, c.get_unasgn_vars()[0]))

    return constraints


def dequeue(queue):
    removed = queue[0]
    new_queue = queue[1:]
    return (removed, new_queue)


def enqueue(queue, item):
    queue.append(item)


def empty(queue):
    queue = []


def enqueueTamperedConstraints(GAC_queue, csp, v):

    constraints = csp.get_cons_with_var(v)
    for c in constraints:
        if c not in GAC_queue:
            enqueue(GAC_queue, c)


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

    DWO = False
    pruned = []

    for (c, x) in getFCConstraints(csp, newVar):

        for d in x.cur_domain():

            # FOR DEBUGGING, TODO: REMOVE AFTER
            if newVar.name == "V11" and x.name == "V13" and d == 3:
                pass

            if falsifies(csp, c, x, d) and (x, d) not in pruned:
                x.prune_value(d)
                pruned.append((x, d))

        if x.cur_domain_size() == 0:
            DWO = True
            break

    return (not DWO, pruned)


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    DWO = False
    pruned = []

    GAC_queue = csp.get_all_cons()

    while GAC_queue != []:
        c, GAC_queue = dequeue(GAC_queue)
        for v in c.get_scope():
            for d in v.cur_domain():
                if not c.has_support(v, d):
                    v.prune_value(d)

                    if (v, d) not in pruned:
                        pruned.append((v, d))

                    if v.domain_size() == 0:
                        empty(GAC_queue)
                        DWO = True
                        return (DWO, pruned) # TODO
                    else:
                        enqueueTamperedConstraints(GAC_queue, csp, v)

    return (DWO, pruned)


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT

    vars = csp.get_all_vars()
    mrv = -1

    for v in vars:
        if mrv == -1:
            mrv = (v, v.cur_domain_size())
        else:
            if v.cur_domain_size() < mrv[1]:
                mrv = (v, v.cur_domain_size())

    return mrv[0]
