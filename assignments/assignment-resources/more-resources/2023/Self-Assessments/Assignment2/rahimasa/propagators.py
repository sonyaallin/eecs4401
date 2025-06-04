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
    if newVar is None:
        constraints= csp.cons
    else:
        constraints = csp.vars_to_cons[newVar]
    prunes=[]
    final = True
    # print(csp.print_soln())
    for c in constraints:
        if c.get_n_unasgn() == 1:
            vals=[]
            v_index=None
            for v in range(len(c.scope)):
                if c.scope[v].is_assigned():
                    vals.append(c.scope[v].assignedValue)
                else:
                    vals.append(None)
                    v_index= v
            possible = False
            # print(len( c.scope[v_index].cur_domain()))
            for d in c.scope[v_index].cur_domain():
                # c.scope[v_index].assign(d)
                vals[v_index]=d
                if not c.check(vals):
                    # print(vals)
                    # print(c.sat_tuples)
                    # print(vals, v_index, c.sat_tuples)
                    # print((c.scope[v_index],d))
                    prunes.append((c.scope[v_index],d))
                    # Check to see if this is neccary
                    # c.scope[v_index].unassign()
                    c.scope[v_index].prune_value(d)
            if c.scope[v_index].cur_domain_size()==0:
                # print("False", prunes, vals, v_index, c)
                # print(c.sat_tuples)
                final = False
                return False, prunes
    return final, prunes
    # pass


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    # IMPLEMENT
    if newVar is None:
        constraints = csp.cons
    else:
        constraints= csp.vars_to_cons[newVar]
    prunes=[]
    while constraints !=[]:
        c = constraints[0]
        for v in c.scope:
            for d in v.cur_domain():
                # v.assign_value(d)
                if not c.has_support(v, d):
                    v.prune_value(d)
                    prunes.append((v,d))
                    if v.cur_domain_size()==0:
                        return False, prunes
                    else:
                        for cons in csp.vars_to_cons[v]:
                            if cons not in constraints:
                                constraints.append(cons)
        constraints= constraints[1:]
    return True, prunes
def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    smallest = [], float('inf')
    for var in csp.vars:
        if var.cur_domain_size()< smallest[1] and not var.is_assigned():
            smallest= [var], var.cur_domain_size()
        elif var.cur_domain_size()== smallest[1] and not var.is_assigned():
            smallest[0].append(var)
    biggest = None, -1
    for var in smallest[0]:
        cons = csp.vars_to_cons[var]
        if len(cons)> biggest[1]:
            biggest= var, len(cons)
    return biggest[0]
