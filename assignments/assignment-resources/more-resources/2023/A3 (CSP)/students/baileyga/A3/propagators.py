#Look for #IMPLEMENT tags in this file. These tags indicate what has
#to be implemented to complete problem solution.  
from collections import deque
import math

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
    var_ordering(csp)
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

def getVals(con):
    '''Gets the current values of the variables in a constraint
    @return (values, indexes of unnasigned variables)'''
    vals = []
    vars = con.get_scope()
    index = []
    for var in vars:
        vals.append(var.get_assigned_value())
        # want the indexes to insert to for later:
        if vals[-1] == None:
            index.append(len(vals)-1)
    return vals, index

def prop_FC(csp, newVar=None):
    '''Do forward checking. That is check constraints with 
       only one uninstantiated variable. Remember to keep 
       track of all pruned variable,value pairs and return '''
    
    prunings = []
    cons = []
    if newVar: #Normal search
        cons = csp.get_cons_with_var(newVar)
    else:
        #Search preprocessing
        '''for forward checking (where we only check constraints with one
        remaining variable)
        we look for unary constraints of the csp (constraints whose scope 
        contains only one variable) and we forward_check these constraints.'''
        cons = csp.get_all_cons()

    for c in cons:
        if c.get_n_unasgn() == 1: #Do forward checking on conditions with 1 var left
            vals, index = getVals(c)
            var = c.get_unasgn_vars()[0]
            for val in var.cur_domain():
                vals[index[0]] = val
                if not c.check(vals):
                    var.prune_value(val)
                    prunings.append((var,val))
            if var.cur_domain() == []: #DWO
                return False, prunings
        elif newVar and c.get_n_unasgn() == 0: #Check all completed conditions are fulfilled
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals): #Invalid assignment
                return False, prunings 
    return True, prunings 

def prop_GAC(csp, newVar=None):
    '''Do GAC propagation. If newVar is None we do initial GAC enforce 
       processing all constraints. Otherwise we do GAC enforce with
       constraints containing newVar on GAC Queue'''
    prunings = []
    gacQueue = None
    if not newVar: #Search preprocessing
        # for gac we establish initial GAC by initializing the GAC queue
        # with all constaints of the csp
        cons = csp.get_all_cons()
        gacQueue = deque(cons,maxlen=len(cons))
    else: #Normal search
        cons = csp.get_cons_with_var(newVar)
        gacQueue = deque(cons,maxlen=len(csp.get_all_cons()))
        
    while len(gacQueue) > 0:
            c = gacQueue.pop()
            vars = c.get_scope()
            for var in vars:
                for val in var.cur_domain():
                    if not c.has_support(var,val):
                        var.prune_value(val)
                        prunings.append((var,val))
                        if var.cur_domain() == []: #DWO
                            return False, prunings
                        else:
                            for con in csp.get_cons_with_var(var):
                                if con not in gacQueue: #This might be really inneficient?
                                    gacQueue.append(con)
    return True, prunings   

def ord_mrv(csp):
    ''' return variable according to the Minimum Remaining Values heuristic '''
    # This breaks ties by using the first element it sees, i.e. the one that is earlier in the var list
    return min(csp.get_all_unasgn_vars(), key=lambda x: x.cur_domain_size())

	