# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete problem solution.

class Queue():
    """Bare bones queue class"""
    def __init__(self):
        self.queue = []

    def is_empty(self):
        return len(self.queue) == 0

    def push(self, item):
        if item not in self.queue:
            self.queue.append(item)

    def pull(self):
        if not self.is_empty():
            return self.queue.pop(0)

    def empty(self):
        self.queue = []


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
from A2.cspbase import Variable


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


def prop_FC_old(csp, newVar=None):
    """Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var,
       only check constraints containing newVar"""

    # print("Got Here 3")
    sol_found = False

    # print(csp.get_all_unasgn_vars())

    if len(csp.get_all_unasgn_vars()) == 0:  # i.e all are already assigned
        for var in csp.get_all_vars():
            print(var.get_assigned_value())
        return True, []

    if newVar is not None:
        var = newVar
    else:
        var = ord_mrv(csp)  # This is the next variable to be assigned

    # print("Got Here 2")

    pruned_lst = []

    for elem in var.cur_domain():
        pruned = {}
        var.assign(elem)
        # print(f'Assigned value of {elem} to {var.name}')
        dwo_occ = False
        # print("Got Here 1")
        if newVar is None:
            valid_const = get_val_const(csp, None)
        else:
            valid_const = get_val_const(csp, var)

        # print(f'Variable of Concern: {var}, valid Constraints: {[str(c) for c in valid_const]}')

        for const in valid_const:
            # print(f'Checking This Constraint: {const}')
            x = const.get_unasgn_vars()[0]
            check = fc_check(const, x)
            # check is a tuple, the first element is the success indicator of
            # the FCcheck, the second is the pruned values
            # DONE We need to at some point extend check[1] to x's list in the
            # pruned dictionary
            # print(f'FC Check Came back with this result: {check}')

            if x not in pruned.keys():
                pruned[x] = check[1]
            else:
                pruned[x].extend(check[1])
            for pruned_item in check[1]:
                # print(f'Pruning Value {pruned_item} from {x}')
                pruned_lst.append((x, pruned_item))

            if check[0] == "DWO":
                # print("We Have DWO")
                dwo_occ = True
                break
        if not dwo_occ:
            sol_found, new_pruned = prop_FC(csp, var)
            pruned_lst.extend(new_pruned)
        for v, vals in pruned.items():
            for val in vals:
                # print(f'Unpruning value {val} from {v}')
                v.unprune_value(val)

    var.unassign()
    # print("Dead End?")
    return sol_found, pruned_lst


def prop_FC(csp, newVar=None):
    if newVar is None:
        return prop_FC_helper(csp, newVar, [])
    return kinda_BT(csp, newVar)


def kinda_BT(csp, newVar=None):
    """
    Most Likely newVar will not be None
    """
    if newVar is None:
        return False, []  # Most likely this case has been taken care of
    total_prune = []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 1:
            unasgn = c.get_unasgn_vars()[0]
            status, to_prune = fc_check(c, unasgn)  # "", []
            if status == "DWO":
                for elem in to_prune:
                    unasgn.unprune_value(elem)
                    total_prune.append((unasgn, elem))
                return False, []

    for elem in total_prune:
        elem[0].prune_value(elem[1])
    return True, total_prune


def prop_FC_helper(csp, newVar, pruned_sf):
    """Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var,
       only check constraints containing newVar"""

    # print("Got Here 3")
    sol_found = False

    # print(csp.get_all_unasgn_vars())

    if len(csp.get_all_unasgn_vars()) == 0:  # i.e all are already assigned
        for var in csp.get_all_vars():
            print(var.get_assigned_value())
        return True, []

    var = ord_mrv(csp)  # This is the next variable to be assigned

    # print("Got Here 2")

    for elem in var.cur_domain():
        pruned = {}
        var.assign(elem)
        # print(f'Assigned value of {elem} to {var.name}')
        dwo_occ = False
        # print("Got Here 1")
        # if newVar is None:
            # valid_const = get_val_const(csp, None)
        # else:
        valid_const = get_val_const(csp, var)

        # print(f'Variable of Concern: {var}, valid Constraints: {[str(c) for c in valid_const]}')

        for const in valid_const:
            # print(f'Checking This Constraint: {const}')
            x = const.get_unasgn_vars()[0]
            check = fc_check(const, x)
            # check is a tuple, the first element is the success indicator of
            # the FCcheck, the second is the pruned values
            # DONE We need to at some point extend check[1] to x's list in the
            # pruned dictionary
            # print(f'FC Check Came back with this result: {check}')

            if x not in pruned.keys():
                pruned[x] = check[1]
            else:
                pruned[x].extend(check[1])
            for pruned_item in check[1]:
                # print(f'Pruning Value {pruned_item} from {x}')
                pruned_sf.append((x, pruned_item))

            if check[0] == "DWO":
                # print("We Have DWO")
                dwo_occ = True
                break
        if not dwo_occ and (newVar is None or newVar != var):  # This element of the domain has potential
            temp_sol_found, pruned_f = prop_FC_helper(csp, None, pruned_sf)
            sol_found = sol_found or temp_sol_found
            """
            if sol_found and newVar is None and len(csp.get_all_unasgn_vars()) == 0:
                for variable in csp.get_all_vars():
                    variable.unassign()
                return True, pruned_sf"""
        for v, vals in pruned.items():
            for val in vals:
                # print(f'Unpruning value {val} from {v}')
                v.unprune_value(val)
                if (v, val) in pruned_sf:
                    pruned_sf.remove((v, val))

    var.unassign()
    # print("Dead End?")
    return sol_found, pruned_sf


def fc_check(const, var):  # DONE

    # print(f'Now doing FCCheck on variable: {var}')

    removed_values = []

    for dom in var.cur_domain():
        vals = []
        for var_scoped in const.get_scope():
            if var_scoped != var:
                vals.append(var_scoped.get_assigned_value())
            else:
                vals.append(dom)

        # Now vals refers to a temporary list of values where the temporariness
        # is coming from the fact that we are trading in n out the value of var

        if not const.check(vals):  # This element of the dom invalidates const
            removed_values.append(dom)  # Store the fact that we are pruning dom
            var.prune_value(dom)  # Actually Prune dom

    if var.cur_domain_size() == 0:
        return "DWO", removed_values
    else:
        return "ok", removed_values


def get_val_const(csp, newVar):
    """
    Given a csp and variable, find and return the constrains that have only
    one unassigned variable.
    """
    if newVar is None:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(newVar)

    val_const = []
    for con in constraints:
        num_unassigned = con.get_n_unasgn()

        # Now num_unassigned referes to the number of unassigned variables in
        # the scope of cons

        if num_unassigned == 1:
            val_const.append(con)
            # print(f'Unassigned: {con.get_unasgn_vars()[0]}')

    # Now val_const refers to the constraints with only one unassigned varaible
    # in scope

    return val_const


def GAC_Enforce(csp, gac_q: Queue, pruned_sf):
    while not gac_q.is_empty():
        c = gac_q.pull()
        for var in c.get_scope():
            for elem in var.cur_domain():
                works = can_satisfy(c, var, elem)
                if not works:
                    var.prune_value(elem)
                    pruned_sf.append((var, elem))
                    if var.cur_domain_size() == 0:
                        gac_q.empty()
                        return "DWO", pruned_sf  # We need to make a helper function.
                    else:
                        for const in csp.get_all_cons():
                            if var in const.get_scope():
                                gac_q.push(const)
    return True, pruned_sf


def GAC_prepocess(csp, newVar, pruned_sf):
    """This is when newVar is None so we do preprocessing"""
    assert newVar is None

    gac_q = Queue()

    for constraint in csp.get_all_cons():
        gac_q.push(constraint)

    enforced, pruned_sf = GAC_Enforce(csp, gac_q, pruned_sf)

    if enforced == "DWO":
        for pair in pruned_sf:
            pair[0].unprune_value(pair[1])
        return False, []
    return True, pruned_sf


def get_tups(vars, variable, val):
    if len(vars) == 0:
        return [()]

    final = []
    one_less = get_tups(vars[1:], variable, val)

    if vars[0] == variable:
        for tup in one_less:
            temp = list(tup)
            final.append([val] + temp)
    else:
        for elem in vars[0].cur_domain():
            for tup in one_less:
                temp = list(tup)
                final.append([elem] + temp)

    return final


def can_satisfy(constraint, variable, val):
    """
    Given a val assignment to variable, can we find a tuple to satisfy constrain
    """
    tups = get_tups(constraint.get_scope(), variable, val)

    for tup in tups:
        if constraint.check(tup):
            return True

    return False



def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    if newVar is None:
        return GAC_prepocess(csp, newVar, [])
    return prop_GAC_helper(csp, newVar, [])


def prop_GAC_helper(csp, newVar, pruned_sf):
    if len(csp.get_all_unasgn_vars()) == 0:
        csp.print_soln()
        return True, pruned_sf

    consts = get_val_const(csp, newVar)
    gac_q = Queue()

    # At this point we knew that newVar is None and that is assigned.
    assert newVar.is_assigned()

    for elem in newVar.cur_domain():
        if elem != newVar.get_assigned_value():
            newVar.prune_value(elem)
    for const in csp.get_cons_with_var(newVar):
        gac_q.push(const)

    enforced, pruned_f = GAC_Enforce(csp, gac_q, pruned_sf)

    if enforced == "DWO":
        pruned_by_GAC = list(set(pruned_f) - set(pruned_sf))
        for elem in pruned_by_GAC:
            elem[0].unprune_value(elem[1])
        return False, pruned_sf
    return True, pruned_f


def ord_mrv(csp) -> Variable:  # DONE
    """ return variable according to the Minimum Remaining Values heuristic """
    # IMPLEMENT

    min_var = None

    for var in csp.get_all_unasgn_vars():
        if min_var is None:
            min_var = var
        elif min_var.cur_domain_size() > var.cur_domain_size():
            min_var = var

    return min_var
