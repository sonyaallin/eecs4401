# Look for #IMPLEMENT tags in this file. These tags indicate what has
# to be implemented to complete problem solution.
import itertools

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

    if not newVar:  # if newVar is none
        return True, []
    for c in csp.get_cons_with_var(newVar):  # return a list of cons with var
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []


# Helper FC_check
# de
def FC_check(cons, var):
    """
    input: single constrain and a single variable
    that constrain has all the var assign
    output: bool, list of pruned (var, val)
    """
    DOW = False
    prune_lst = []
    for d in var.cur_domain():
        if not cons.has_support(var, d):
            var.prune_value(d)
            prune_lst.append((var, d))
    if var.cur_domain_size() == 0:
        DOW = True
    return DOW, prune_lst


def prop_FC(csp, newVar=None):
    '''
    Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var,
       only check constraints containing newVar
    '''
    DWO_occur = False
    pruned_lst = []
    if not newVar:
        for c in csp.get_all_cons():
            if c.get_n_unasgn() == 1:
                un_ass_var = c.get_unasgn_vars()
                DWO_occur, tmp_lst = FC_check(c, un_ass_var[0])
                pruned_lst.extend(tmp_lst)
                if DWO_occur:
                    break
        return not DWO_occur, pruned_lst

    for c in csp.get_cons_with_var(newVar):  # return a list of cons with var
        # FC check
        if c.get_n_unasgn() == 1:
            un_ass_var = c.get_unasgn_vars()
            DWO_occur, tmp_lst = FC_check(c, un_ass_var[0])
            pruned_lst.extend(tmp_lst)
            if DWO_occur:
                break
    return not DWO_occur, pruned_lst


# HELPER FOR GAC ENFORCE
def helper_gac_lst_assignment(index: int, index_value: int, scop_size: int,
                              grid_side: int):
    """
    input:
    index for variable position in scope
    index value in its curr domain

    """
    re_lst = []
    side_lst = list(range(1, grid_side + 1))
    iter = itertools.combinations_with_replacement(side_lst, scop_size)
    for tu in iter:
        if tu[index] == index_value:
            re_lst.append(tu)

    side_lst.reverse()
    iter2 = itertools.combinations_with_replacement(side_lst, scop_size)
    for tu in iter2:
        if tu[index] == index_value:
            re_lst.append(tu)
    return re_lst


# HELPER GAC_ENFORCE
def GAC_Enforce(gac_queue, grid_side: int):
    """
    input: a list of gac queue
    return a pruned lst pair and DWO status

    """
    pruned_pair = []
    DWO = False

    for cons in gac_queue:
        scope_lst = cons.get_scope()
        for i in range(len(scope_lst)):
            var = scope_lst[i]
            cur_dom_lst = var.cur_domain()
            for j in range(var.cur_domain_size()):
                curr_val = cur_dom_lst[j]
                tu_potential = helper_gac_lst_assignment(i, curr_val,
                                                         len(scope_lst),
                                                         grid_side)
                found_ass = False
                for lst_val in tu_potential:
                    if cons.check(lst_val):
                        found_ass = True
                        break
                if not found_ass and var.in_cur_domain(curr_val):
                    var.prune_value(curr_val)
                    pruned_pair.append((var, curr_val))
                    if var.cur_domain_size() == 0:
                        DWO = True
                        return DWO, pruned_pair
    return DWO, pruned_pair


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    # side = math.sqrt(len(csp.get_all_vars()))
    # side = int(side)
    # if newVar is None:
    #     DWOoccur, pruned_pair = GAC_Enforce(csp.get_all_cons(), side)
    #     return not DWOoccur, pruned_pair
    # DWOoccur, pruned_pair = GAC_Enforce(csp.get_cons_with_var(newVar), side)
    # return not DWOoccur, pruned_pair
    return prop_FC(csp, newVar)


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    var_lst = csp.get_all_unasgn_vars().copy()
    cur_d_size = float('inf')
    store_index = None
    for i in range(len(var_lst)):
        var = var_lst[i]
        if var.cur_domain_size() < cur_d_size:
            cur_d_size = var.cur_domain_size()
            store_index = i
    return var_lst[store_index]
