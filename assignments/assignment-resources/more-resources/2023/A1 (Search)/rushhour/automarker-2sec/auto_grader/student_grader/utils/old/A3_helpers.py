import sys
from cspbase import *
from propagators import *
import itertools
import traceback

def sum_big1(xdom,ydom,zdom):
    lister = [] 
    for xval in xdom:
        for yval in ydom:
            for zval in zdom:
                if xval + yval > zval:
                    lister.append( (xval,yval,zval) )
    return lister

def minus_pos(dom1,dom2):
    lister = [] 
    for xval in dom1:
        for yval in dom2:
            if yval - xval > 0:
                lister.append([xval,yval])
    return lister

def plus_double_4(dom1,dom2):
    lister = [] 
    for xval in dom1:
        for yval in dom2:
            if xval + 2*yval > 4:
                lister.append([xval,yval])
    return lister

def sum_less5(dom1,dom2):
    lister = [] 
    for xval in dom1:
        for yval in dom2:
            if xval + yval < 5:
                lister.append([xval,yval])
    return lister

def less2(xdom,zdom):
    lister = [] 
    for xval in xdom:
        for zval in zdom:
            if xval <= zval:
                lister.append([xval,zval])
    return lister

def queensCheck(qi, qj, i, j):
    '''Return true if i and j can be assigned to the queen in row qi and row qj 
       respectively. Used to find satisfying tuples.
    '''
    return i != j and abs(i-j) != abs(qi-qj)

def sum1(dom1,dom2,dom3):
	lister = [] 
	for xval in dom1:
		for yval in dom2:
			a = xval + yval
			if a in dom3:
				lister.append([xval,yval,xval+yval])
	return lister

def less1(domz,domw):
	lister = [] 
	for zval in domz:
		for wval in domw:
			if zval <= wval:
				lister.append([wval,zval])
	return lister

def sum_less1(xdom,ydom,zdom):
	lister = [] 
	for xval in xdom:
		for yval in ydom:
			for zval in zdom:
				if xval + yval < zval:
					lister.append( (xval,yval,zval) )
	return lister

def minus_even(dom1,dom2):
    lister = [] 
    for xval in dom1:
        for yval in dom2:
            if (xval - yval) % 2 == 0:
                lister.append([xval,yval])
    return lister

def val_predictable(csp,var):
    '''
    val_arbitrary(csp,var):
    A val_ordering function that takes CSP object csp and Variable object var,
    and returns a value in var's current domain arbitrarily.
    '''
    return var.curdom[0] 

def nQueens(n):
    '''Return an n-queens CSP'''
    i = 0
    dom = []
    for i in range(n):
        dom.append(i+1)

    vars = []
    for i in dom:
        vars.append(Variable('Q{}'.format(i), dom))

    cons = []    
    for qi in range(len(dom)):
        for qj in range(qi+1, len(dom)):
            con = Constraint("C(Q{},Q{})".format(qi+1,qj+1),[vars[qi], vars[qj]]) 
            sat_tuples = []
            for t in itertools.product(dom, dom):
                if queensCheck(qi, qj, t[0], t[1]):
                    sat_tuples.append(t)
            con.add_satisfying_tuples(sat_tuples)
            cons.append(con)
    
    csp = CSP("{}-Queens".format(n), vars)
    for c in cons:
        csp.add_constraint(c)
    return csp
    
def check_solution(hitori_variable_array):

    if not isinstance(hitori_variable_array[0], list):
            print("0")
            return False

    for i in range(len(hitori_variable_array)):
        row_sol = []
        blacks = [False] * len(hitori_variable_array)
        #print(hitori_variable_array)
        for j in range(len(hitori_variable_array)):
            if hitori_variable_array[i][j].get_assigned_value() != 0:
                row_sol.append(hitori_variable_array[i][j].get_assigned_value())
                blacks[j] = False
            else:
                if blacks[j - 1] or blacks[j]:
                    print("1")
                    return False
                else:
                    blacks[j] = True
        if not check_list(row_sol):
            print("2")
            return False

    for i in range(len(hitori_variable_array)):
        row_sol = []
        blacks = [False] * len(hitori_variable_array)
        for j in range(len(hitori_variable_array)):
            if hitori_variable_array[j][i].get_assigned_value() != 0:
                row_sol.append(hitori_variable_array[j][i].get_assigned_value())
                blacks[j] = False
            else:
                if blacks[j - 1] or blacks[j]:
                    print("3")
                    return False
                else:
                    blacks[j] = True
        if not check_list(row_sol):
            print("4")
            return False

    return True

##Helper function that checks if a given list is valid
def check_list(solution_list):
    return len(solution_list) == len(set(solution_list))