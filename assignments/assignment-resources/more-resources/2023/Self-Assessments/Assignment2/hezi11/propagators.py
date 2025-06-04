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
    dead_end = False
    var_val_lst = []

    # forward check all constraints with one uninstantiated variable
    if newVar is None:
        c_lst = csp.get_all_cons()
        for c in c_lst:
            var_in_c = c.get_scope
            if var_in_c == 1:
                dead_end, var_val_lst = FC(c, var_val_lst)
                if not dead_end:
                    return dead_end, var_val_lst
        # no dead_end was found
        return dead_end, var_val_lst

    # only check constraints containing newVar
    if newVar is not None:
        var_c_lst = csp.get_cons_with_var(newVar)
        for c in var_c_lst:
            if c.get_n_unasgn() == 1:
                dead_end, var_val_lst = FC(c, var_val_lst)
                if not dead_end:
                    return dead_end, var_val_lst
        return dead_end, var_val_lst


def FC(c, var_val):
    """
    Do forward checking with given c.
    Return a (Bool, List[Tuple[Variable, Value]]), where the first item is False
    iff a dead_end is found, the second item is based on var_val, add new variable,
    Value pair to var_val if there is any.
    """
    # the unassigned variable
    unasgn_var = c.get_unasgn_vars()[0]

    # the current domain of this unassigned variable
    unasgn_var_d = unasgn_var.cur_domain()

    # iterate through the domain to assign each value to variable and check
    # if condition is met
    for val in unasgn_var_d:
        val.assign(val)
        var_lst = c.get_scope()
        val_lst = []
        for v in var_lst:
            val_lst.append(v.get_assigned_value())
        if not c.check(val_lst):
            var_val.append((unasgn_var, val))
            unasgn_var.prune(val)
        unasgn_var.unassign()

    # at least one solution found
    if unasgn_var.cur_domain_size != 0:
        return True, var_val
    else:
        return False, var_val



def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    GAC_q = Queue()
    var_val_lst = []
    dead_end = False

    # do initial GAC enforce processing all constraints
    if newVar is None:
        c_lst = csp.get_all_cons()
        # enqueue all the constraint into GAC_q
        for c in c_lst:
            GAC_q.enqueue(c)
        dead_end, var_val_lst = GAC_enforce(csp, var_val_lst, GAC_q)
        if not dead_end:
            return dead_end, var_val_lst
        return dead_end, var_val_lst

    if newVar is not None:
        c_lst = csp.get_cons_with_var(newVar)
        for c in c_lst:
            GAC_q.enqueue(c)
        dead_end, var_val_lst = GAC_enforce(csp, var_val_lst, GAC_q)
        if not dead_end:
            return dead_end, var_val_lst
        return dead_end, var_val_lst


def GAC_enforce(csp, var_val, gac_q):
    """
    GAC enforce on given gac_q.
    """
    # check all constraint in gac_q until it is empty
    while not gac_q.isEmpty():
        c = gac_q.dequeue
        var_lst = c.get_scope()
        # iterate through all variables
        for v in var_lst:
            # if variables is assigned, pass
            if v.is_assigned():
                continue
            # iterate through all values in current domain of this variable
            for val in v.cur_domain():
                v.assign(val)
                # check if constraint has support on this variable, value pair
                if not c.has_support(v, val):
                    var_val.append((v, val))
                    v.prune(val)
                    v.unassign()
                    # check for dead_end
                    if v.cur_domain_size == 0:
                        gac_q.empty()
                        return False, var_val
                else:
                    # iterate through constraints in this variables to check
                    # if any of its constraints is not in gac_q, if so, add this
                    # constraint to gac_q for checking later in the program
                    for new_c in csp.get_cons_with_var(v):
                        if new_c not in gac_q:
                            gac_q.enqueue(new_c)

    # if no dead end was found
    return True, var_val



def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    # get all currently unassigned variables
    var_lst = csp.get_all_unasgn_vars()

    # find min domain
    min_d = float('inf')
    for v in var_lst:
        curdom_size = v.cur_domain_size()
        if curdom_size <= min_d:
            min_d = curdom_size

    # find variables with min domain
    var_min_d = []
    for v in var_lst:
        curdom_size = v.cur_domain_size()
        if curdom_size == min_d:
            var_min_d.append(v)

    # if there is only one variable with min domain
    if len(var_min_d) == 1:
        return var_min_d[0]
    else:
        # find min constraint
        min_c = float('inf')
        for v in var_min_d:
            if len(csp.get_cons_with_var(v)) < min_c:
                min_c = len(csp.get_cons_with_var(v))
        # find variables with min constraint
        var_min_c = []
        for v in var_min_d:
            curdom_size = v.cur_domain_size()
            if curdom_size == min_c:
                var_min_c.append(v)
        return var_min_c[0]


class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

    def empty(self):
        while not self.isEmpty():
            self.dequeue()
