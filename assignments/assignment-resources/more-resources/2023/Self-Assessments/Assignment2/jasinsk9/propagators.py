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
import numpy as np


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
    pruned = []
    if newVar is None:
        for constraint in csp.get_all_cons():
            if constraint.get_n_unasgn() == 1:
                var = constraint.get_unasgn_vars()[0]
                fc = fcheck(var, constraint)
                if fc[0] == 'DWO':
                    pruned += fc[1]
                    for tup in pruned:
                        tup[0].unprune_value(tup[1])
                    return False, []
                else:
                    pruned += fc[1]
        return True, pruned
    else:
        for constraint in csp.get_all_cons():
            if constraint.get_n_unasgn() == 1 and newVar in constraint.scope:
                var = constraint.get_unasgn_vars()[0]
                fc = fcheck(var, constraint)
                if fc[0] == 'DWO':
                    pruned += fc[1]
                    for tup in pruned:
                        tup[0].unprune_value(tup[1])
                    return False, []
                else:
                    pruned += fc[1]
        return True, pruned

def fcheck(var, constraint):
    scope = constraint.scope.copy()
    index = 0
    pruned = []
    for i in range(len(scope)):
        if scope[i].is_assigned():
            scope[i] = scope[i].get_assigned_value()
        else:
            index = i
    for value in var.cur_domain():
        scope[index] = value
        if not constraint.check(scope):
            var.prune_value(value)
            pruned.append((var, value))
    if var.cur_domain() == []:
        return 'DWO', pruned
    return 'Good', pruned


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    queue = []
    if newVar is None:
        for constraint in csp.get_all_cons():
            queue.append(constraint)
        gc, pruned = gaccheck(csp, queue, newVar)
        if gc == 'DWO':
            for tup in pruned:
                tup[0].unprune_value(tup[1])
            return False, []
        else:
            return True, pruned
    else:
        for constraint in csp.get_all_cons():
            if newVar in constraint.scope:
                queue.append(constraint)
        gc, pruned = gaccheck(csp, queue, newVar)
        if gc == 'DWO':
            for tup in pruned:
                tup[0].unprune_value(tup[1])
            return False, []
        else:
            return True, pruned



def gaccheck(csp, q, variable):
    pruned = []
    while q:
        c = q.pop(0)
        for var in c.get_scope():
            if var != variable:
                for value in var.cur_domain():
                    if var.is_assigned():
                        break;
                    test = c.scope.copy()
                    for i in range(0, len(test)):
                        if test[i].is_assigned():
                            test[i] = test[i].get_assigned_value()
                    test[test.index(var)] = value
                    civ = check_if_value(test, c)
                    if not civ:
                        var.prune_value(value)
                        pruned.append((var, value))
                        if var.cur_domain() == []:
                            return 'DWO', pruned
                        else:
                            for constraint in csp.get_all_cons():
                                if var in constraint.scope:
                                    q.append(constraint)
    return 'Good', pruned



def check_if_value(test, c):
    if all(isinstance(var, int) for var in test):
        return True
    possible = []
    possibilities = get_all_possible(test, possible, c)
    if possibilities is None:
        return False
    for poss in possibilities:
        if tuple(poss) in c.sat_tuples:
            return True
    return False

def get_all_possible(test, possible, c):
    check = False
    for item in test:
        if not isinstance(item, int):
            if possible:
                possible.pop(0)
            check = True
            if c.name.startswith('Row') or c.name.startswith('Col'):
                for value in item.cur_domain():
                    if value not in test:
                        temp = test.copy()
                        temp[temp.index(item)] = value
                        possible.append(temp)
                        if tuple(temp) in c.sat_tuples.keys():
                            return possible
                for poss in possible:
                    possible = get_all_possible(poss, possible, c)
                    return possible
            else:
                for value in item.cur_domain():
                    temp = test.copy()
                    temp[temp.index(item)] = value
                    possible.append(temp)
                    if tuple(temp) in c.sat_tuples.keys():
                        return possible
                for poss in possible:
                    possible = get_all_possible(poss, possible, c)
                    return possible
    if not check:
        return possible


def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    variables = csp.get_all_unasgn_vars()
    chosen = variables[0]
    for var in variables:
        if var.domain_size() < chosen.domain_size():
            chosen = var
    return chosen
