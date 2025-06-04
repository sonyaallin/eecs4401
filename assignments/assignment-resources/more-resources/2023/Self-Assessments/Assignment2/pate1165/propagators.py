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


from cmath import inf


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


def FCCheck(C,X):  
    prunes = []
    for val in X.cur_domain():
        vals = []
        vars = C.get_scope()
        X.assign(val)
        for var in vars:
            vals.append(var.get_assigned_value())  

        if C.check(vals) == False:
            X.prune_value(val)
            prunes.append((X,val))
        X.unassign()
    if X.cur_domain_size() == 0:
        return 'dwo',prunes
    return 'good',prunes


def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with
       only one uninstantiated variable. Remember to keep
       track of all pruned variable,value pairs and return.
       If newVar is None, you must forward check all constraints
       with one uninstantiated variable. Else, if newVar=var, 
       only check constraints containing newVar'''
    # Fc(Level Function)
    
    prunes = []
    if newVar == None:
        lst = csp.get_all_cons()
    else:
        lst = csp.get_cons_with_var(newVar)



    for cons in lst:
        if cons.get_n_unasgn() == 1:
            var = cons.get_unasgn_vars()[0]
            dw,ret_prunes = FCCheck(cons,var)
            prunes.extend(ret_prunes)
            if dw == 'dwo':
                return False, prunes
    return True,prunes
                    # if cons.check():
                    #     vals=[]
                    #     vars = cons.get_scope()
                    #     for var in vars:
                    #         vals.append(var.get_assigned_value())
                    #     if cons.check(vals) == False: #chekc if u need to appendn new val
                    #         dw = True
                    #         break
    #         if dw:
    #             csp.restoreValues(prunes)



        

    # for cons in lst:
    #     if cons.get_n_unasgn() == 1:
    #         # vars = cons.get_scope()
    #         vals = []
    #         values = csp.cur_domain()
    #         vars = cons.get_scope()
    #         for var in vars:
    #             vals.append(var.get_assigned_value())
    #         for val in values:
    #             vals.append(val)
    #             if not cons.check(vals):
    #                 csp.prune_value(val.get_assigned_value())
    #                 prunes.append(val.get_assigned_value())
    #             vals.pop()
                        
    #     if csp.cur_domain_size() == 0:
    #         return False, prunes

    # return True, prunes

 


def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    if newVar == None:
        gac_queue = csp.get_all_cons()
    else:
        gac_queue = csp.get_cons_with_var(newVar)
    prunes_lst = []
    while len(gac_queue) != 0:
        curr_cons = gac_queue.pop(0)

        for var in curr_cons.get_scope():
            for d in var.cur_domain():
                if curr_cons.has_support(var,d) == False:
                    var.prune_value(d)
                    prunes_lst.append((var,d))
                    if var.cur_domain_size() == 0:
                        gac_queue = []
                        return False, prunes_lst
                    else:
                        for x in csp.get_cons_with_var(var):
                            if x not in gac_queue:
                                gac_queue.append(x)
    return True, prunes_lst
    


                        





def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # IMPLEMENT
    mins = csp.get_all_unasgn_vars()[0].cur_domain_size()
    toRet = csp.get_all_unasgn_vars()[0]
    for v in csp.get_all_unasgn_vars():
        if v.cur_domain_size() < mins:
            toRet = v

    return toRet

