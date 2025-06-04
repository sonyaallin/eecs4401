import sys
print(sys.path)
from cspbase import *
import itertools
import traceback
import signal

import futoshiki_csp_soln as sol_futoshiki
import propagators_soln as soln_propagators

#from utils.test_tools import max_grade
#from utilities import TO_exc

#TODO define reasonable timeouts
timeout = 60

def toHandler(signum, frame):
    raise TO_exc()

class TO_exc(Exception):
    pass

def setTO(TOsec):
    signal.signal(signal.SIGALRM, toHandler)
    signal.alarm(TOsec)

########################################
##Necessary setup to generate CSP problems

def queensCheck(qi, qj, i, j):
    '''Return true if i and j can be assigned to the queen in row qi and row qj
       respectively. Used to find satisfying tuples.
    '''
    return i != j and abs(i-j) != abs(qi-qj)

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

def w_eq_sum_x_y_z(wxyz):
    #note inputs lists of value
    w = wxyz[0]
    x = wxyz[1]
    y = wxyz[2]
    z = wxyz[3]
    return(w == x + y + z)

##A simple csp where nothing is pruned via GAC
def even_odd_csp():
    dom = (1,2,3,4)
    vars = []
    vars.append(Variable('X',list(dom)))
    vars.append(Variable('Y',list(dom)))

    con1 = Constraint("X+Y odd",[vars[0],vars[1]])
    sat_tuples = []
    for t in itertools.product(dom,dom):
        if (t[0]+t[1]) % 2 == 1:
            sat_tuples.append(t)
    con1.add_satisfying_tuples(sat_tuples)
    csp = CSP("X + Y odd", vars)
    csp.add_constraint(con1)

    return csp

def three_var_csp():
    dom = (1,2,3,4)
    vars = []
    vars.append(Variable('W',list(dom)))
    vars.append(Variable('X',list(dom)))
    vars.append(Variable('Y',list(dom)))
    vars.append(Variable('Z',list(dom)))

    sat_tuples = []
    con1 = Constraint("W + X < Y",[vars[0],vars[1],vars[2]])
    for t in itertools.product(dom,repeat=3):
        if t[0] + t[1] < t[2]:
            sat_tuples.append(t)

    con1.add_satisfying_tuples(sat_tuples)
    sat_tuples = []
    con2 = Constraint("X + Y < Z",[vars[1],vars[2],vars[3]])
    for t in itertools.product(dom,repeat=3):
        if t[0] + t[1] < t[2]:
            sat_tuples.append(t)
    con2.add_satisfying_tuples(sat_tuples)
    csp = CSP("Tiny comparator",vars)
    csp.add_constraint(con1)
    csp.add_constraint(con2)

    return csp

def three_var_csp2():
    dom = (1,2,3,4)
    vars = []
    vars.append(Variable('W',list(dom)))
    vars.append(Variable('X',list(dom)))
    vars.append(Variable('Y',list(dom)))
    vars.append(Variable('Z',list(dom)))

    sat_tuples = []
    con1 = Constraint("W < X",[vars[0],vars[1]])
    for t in itertools.product(dom,repeat=2):
        if t[0] < t[1]:
            sat_tuples.append(t)

    con1.add_satisfying_tuples(sat_tuples)
    sat_tuples = []
    con2 = Constraint("W + X + Y < Z",[vars[0],vars[1],vars[2],vars[3]])
    for t in itertools.product(dom,repeat=4):
        if t[0] + t[1] + t[2] < t[3]:
            sat_tuples.append(t)
    con2.add_satisfying_tuples(sat_tuples)
    csp = CSP("Tiny comparator2",vars)
    csp.add_constraint(con1)
    csp.add_constraint(con2)

    return csp

##A simple csp where FC & GAC do not return the same thing
##Assign x = 3 when testing.
def tiny_adder_csp():
    dom = (1,2,3,4)
    vars = []
    vars.append(Variable('X',list(dom)))
    vars.append(Variable('Y',list(dom)))
    vars.append(Variable('Z',list(dom)))
    con1 = Constraint("X + Y = Z",[vars[0],vars[1],vars[2]])
    con2 = Constraint("X > Y", [vars[0],vars[1]])
    sat1 = []
    for t in itertools.product(dom,repeat=3):
        if t[0] + t[1] == t[2]:
            sat1.append(t)
    con1.add_satisfying_tuples(sat1)
    sat2 = []
    for t in itertools.product(dom,dom):
        if t[0] > t[1]:
            sat2.append(t)
    con2.add_satisfying_tuples(sat2)

    csp = CSP("Tiny adder",vars)
    csp.add_constraint(con1)
    csp.add_constraint(con2)
    return csp

##Takes in a futoshiki_variable_array, as specified in futoshiki_csp
##variable_array[i][j] is the Variable (object) that represents the value to be placed in cell i,j of the futoshiki board
##Returns True if the solution is a valid solution;
##Returns False otherwise
def check_solution(sudoku_variable_array,greater_thans,less_thans):
    ##check the rows
    for i in range(7):
        row_sol = []
        for j in range(7):
            row_sol.append(sudoku_variable_array[i][j].get_assigned_value())
        if not check_list(row_sol):
            return False
    for j in range(7):
        col_sol = []
        for i in range(7):
            col_sol.append(sudoku_variable_array[i][j].get_assigned_value())
        if not check_list(col_sol):
            return False

    for g in greater_thans:
        if g[0].get_assigned_value() < g[1].get_assigned_value():
            return False

    for l in less_thans:
        if l[0].get_assigned_value() > l[1].get_assigned_value():
            return False

    return True

##Helper function that checks if a given list is valid
def check_list(solution_list):
    solution_list.sort()
    return solution_list == list(range(1,8))



############################################

#@max_grade(1)
##Tests FC after the first queen is placed in position 1.
def test_simple_FC(stu_propagators):
    score = 0

    did_fail = False
    try:
        setTO(timeout)
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(1)
        stu_propagators.prop_FC(queens,newVar=curr_vars[0])
        setTO(0)
        answer = [[1],[3, 4, 5, 6, 7, 8],[2, 4, 5, 6, 7, 8],[2, 3, 5, 6, 7, 8],[2, 3, 4, 6, 7, 8],[2, 3, 4, 5, 7, 8],[2, 3, 4, 5, 6, 8],[2, 3, 4, 5, 6, 7]]
        var_domain = [x.cur_domain() for x in curr_vars]
        for i in range(len(curr_vars)):
            if var_domain[i] != answer[i]:
                #details = "FAILED test_simple_FC\nExplanation:\nFC variable domains should be: %r\nFC variable domains are: %r" % (answer,var_domain)
                details = "Failed simple FC test: variable domains don't match expected results"
                did_fail = True
                break
        if not did_fail:
            details = ""
            score = 1

    except TO_exc:
        details = "Got a TIMEOUT while testing simple FC"
    except Exception:
        details = "One or more runtime errors occurred while testing simple FC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


#@max_grade(1)
##Tests GAC after the first queen is placed in position 1.
def test_simple_GAC(stu_propagators):
    score = 0
    did_fail = False
    try:
        setTO(timeout)
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(1)
        stu_propagators.prop_GAC(queens,newVar=curr_vars[0])
        setTO(0)
        answer = [[1],[3, 4, 5, 6, 7, 8],[2, 4, 5, 6, 7, 8],[2, 3, 5, 6, 7, 8],[2, 3, 4, 6, 7, 8],[2, 3, 4, 5, 7, 8],[2, 3, 4, 5, 6, 8],[2, 3, 4, 5, 6, 7]]
        var_domain = [x.cur_domain() for x in curr_vars]
        for i in range(len(curr_vars)):
            if var_domain[i] != answer[i]:
                #details = "FAILED test_simple_GAC\nExplanation:\nGAC variable domains should be: %r\nGAC variable domains are: %r" % (answer,var_domain)
                details = "Failed simple GAC test: variable domains don't match expected results."
                did_fail = True
                break
        if not did_fail:
            details = ""
            score = 1

    except TO_exc:
        details = "Got a TIMEOUT while testing simple GAC"
    except Exception:
        details = "One or more runtime errors occurred while testing simple GAC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


#@max_grade(1)
##Simple example with 3 queens that results in different pruning for FC & GAC
##Q1 is placed in slot 2, q2 is placed in slot 4, and q8 is placed in slot 8.
##Checking GAC.
def three_queen_GAC(stu_propagators):
    score = 0
    try:
        setTO(timeout)
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(4)
        curr_vars[2].assign(1)
        curr_vars[7].assign(5)
        stu_propagators.prop_GAC(queens)
        setTO(0)

        answer = [[4],[6, 7, 8],[1],[3, 8],[6, 7],[2, 8],[2, 3, 7, 8],[5]]
        var_vals = [x.cur_domain() for x in curr_vars]

        if var_vals != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_vals)
            details = "Failed three queens GAC test: variable domains don't match expected results"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing GAC with three queens"
    except Exception:
        details = "One or more runtime errors occurred while testing GAC with three queens: %r" % traceback.format_exc()

    details = "HERE " + str(score)
    setTO(0)
    return score,details

#@max_grade(1)
##Simple example with 3 queens that results in different pruning for FC & GAC
##Q1 is placed in slot 2, q2 is placed in slot 4, and q8 is placed in slot 8.
##Checking FC.
def three_queen_FC(stu_propagators):
    score = 0
    try:
        setTO(timeout)
        queens = nQueens(8)
        curr_vars = queens.get_all_vars()
        curr_vars[0].assign(4)
        curr_vars[2].assign(1)
        curr_vars[7].assign(5)
        stu_propagators.prop_FC(queens)
        setTO(0)

        answer = [[4],[6, 7, 8],[1],[3, 6, 8],[6, 7],[2, 6, 8],[2, 3, 7, 8],[5]]
        var_vals = [x.cur_domain() for x in curr_vars]

        if var_vals != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_vals)
            details = "Failed three queens FC test: variable domains don't match expected results"

        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing FC with three queens"
    except Exception:
        details = "One or more runtime errors occurred while testing FC with three queens: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(1)
def test_1(propagator, name=""):
    score = 0
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])
        w = Variable('W', [1, 2, 3, 4])

        c1 = Constraint('C1', [x, y, z])
        #c1 is constraint x == y + z. Below are all of the satisfying tuples
        c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

        c2 = Constraint('C2', [w, x, y, z])
        #c2 is constraint w == x + y + z. Instead of writing down the satisfying
        #tuples we compute them

        varDoms = []
        for v in [w, x, y, z]:
            varDoms.append(v.domain())

        sat_tuples = []
        for t in itertools.product(*varDoms):
            #NOTICE use of * to convert the list v to a sequence of arguments to product
            if w_eq_sum_x_y_z(t):
                sat_tuples.append(t)

        c2.add_satisfying_tuples(sat_tuples)

        simpleCSP = CSP("SimpleEqs", [x,y,z,w])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)

        btracker = BT(simpleCSP)
        #btracker.trace_on()

        setTO(timeout)
        btracker.bt_search(propagator)
        curr_vars = simpleCSP.get_all_vars()
        answer = [[2], [1], [1], [4]]
        var_vals = [x.cur_domain() for x in curr_vars]
        setTO(0)
        if var_vals != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_vals)
            details = "Failed while testing a propagator (%s): variable domains don't match expected results" % name
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing a propagator (%s)" % name
    except Exception:
        details = "One or more runtime errors occurred while testing a propagator (%s): %r" % (name, traceback.format_exc())

    setTO(0)
    return score,details

#@max_grade(1)
def test_2(propagator, name=""):
    score = 0
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])

        c1 = Constraint('C1', [x, y, z])
        #c1 is constraint x == y + z. Below are all of the satisfying tuples
        c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

        c2 = Constraint('C2', [x, y])
        #c2 is constraint x + y = 1 mod 2.
        c2.add_satisfying_tuples([[1, 2], [2, 1], [2, 3], [3, 2]])

        c3 = Constraint('C2', [y, z])
        #c3 is constraint y != z
        c3.add_satisfying_tuples([[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]])



        simpleCSP = CSP("ParityEqs", [x,y,z])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        simpleCSP.add_constraint(c3)

        btracker = BT(simpleCSP)
        #btracker.trace_on()

        setTO(timeout)
        btracker.bt_search(propagator)
        setTO(0)
        curr_vars = simpleCSP.get_all_vars()
        answer = [[3], [2], [1]]
        var_vals = [x.cur_domain() for x in curr_vars]
        if var_vals != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_vals)
            details = "Failed while testing a propagator (%s): variable domains don't match expected results" % name
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing a propagator (%s)" % name
    except Exception:
        details = "One or more runtime errors occurred while testing a propagator (%s): %r" % (name, traceback.format_exc())

    setTO(0)
    return score,details

#@max_grade(1)
def test_3(propagator, name=""):
    score = 0
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])

        c1 = Constraint('C1', [x, y, z])
        #c1 is constraint x == y + z. Below are all of the satisfying tuples
        c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

        c2 = Constraint('C2', [y, z])
        #c2 is constraint y + z = 0 mod 2.
        c2.add_satisfying_tuples([[1, 1], [1, 3], [2, 2], [3, 1], [3, 3]])

        c3 = Constraint('C3', [x, y])
        #c2 is constraint x + y = 0 mod 2.
        c3.add_satisfying_tuples([[1, 1], [1, 3], [2, 2], [3, 1], [3, 3]])


        simpleCSP = CSP("ParityEqs", [x,y,z])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        simpleCSP.add_constraint(c3)

        btracker = BT(simpleCSP)
        #btracker.trace_on()

        setTO(timeout)
        btracker.bt_search(propagator)
        setTO(0)
        curr_vars = simpleCSP.get_all_vars()
        answer = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        var_vals = [x.cur_domain() for x in curr_vars]

        if var_vals != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_vals)
            details = "Failed while testing a propagator (%s): variable domains don't match expected results" % name
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing a propagator (%s)" % name
    except Exception:
        details = "One or more runtime errors occurred while testing a propagator (%s): %r" % (name, traceback.format_exc())

    setTO(0)
    return score,details

####################
##################
##NEW TEST CASES

#@max_grade(5)
##A very simple CSP that will return something different for FC and GAC
def test_tiny_adder_FC(stu_propagators):
    score = 0

    did_fail = False
    try:
        csp = tiny_adder_csp()
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(3)
        setTO(timeout)
        stu_propagators.prop_FC(csp,newVar=curr_vars[0])
        setTO(0)

        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[3],[1,2],[1,2,3,4]]

        if var_domain != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_domain)
            details = "Failed small FC test: variable domains don't match expected results"
        else:
            details = ""
            score = 5

    except TO_exc:
        details = "Got a TIMEOUT while testing FC on a small CSP"
    except Exception:
        details = "One or more runtime errors occurred while testing FC on a small CSP: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(5)
def test_tiny_adder_GAC(stu_propagators):
    score = 0

    did_fail = False
    try:
        csp = tiny_adder_csp()
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(3)
        setTO(timeout)
        stu_propagators.prop_GAC(csp,newVar=curr_vars[0])
        setTO(0)

        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[3],[1],[4]]

        if var_domain != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_domain)
            details = "Failed small GAC test: variable domains don't match expected results"
        else:
            details = ""
            score = 5

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC on a small CSP"
    except Exception:
        details = "One or more runtime errors occurred while testing GAC on a small CSP: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(3)
##A simple FC that results in no pruning, even though GAC woudl result in  DWO
def test_no_pruning_FC(stu_prop):
    score = 0

    did_fail = False
    try:
        csp = three_var_csp()
        curr_vars = csp.get_all_vars()
        curr_vars[1].assign(3)
        setTO(timeout)
        stu_prop.prop_FC(csp,newVar=curr_vars[1])
        setTO(0)

        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[1,2,3,4],[3],[1,2,3,4],[1,2,3,4]]

        if var_domain != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_domain)
            details = "Failed FC test that should have resulted in no pruning"
        else:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing simple FC that should result in no pruning"
    except Exception:
        details = "One or more runtime errors occurred while testing simple FC that should result in no pruning: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(3)
##An example where we don't prune anything because we call newVar on a value that is only in w/ two unassigned variables
def test_no_pruning2_FC(stu_prop):
    score = 0

    try:
        csp = three_var_csp2()
        curr_vars = csp.get_all_vars()
        curr_vars[1].assign(1)
        curr_vars[2].assign(1)
        setTO(timeout)
        stu_prop.prop_FC(csp,newVar=curr_vars[2])
        setTO(0)
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[1,2,3,4],[1],[1],[1,2,3,4]]

        if var_domain != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_domain)
            details = "Failed FC test that should have resulted in no pruning"
        else:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing simple FC that should result in no pruning"
    except Exception:
        details = "One or more runtime errors occurred while testing simple FC that should result in no pruning: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(6)
##A simple GAC that results in no pruning, even though some sets of solutions are not viable
def test_no_pruning_GAC(stu_prop):
    score = 0

    try:
        csp = even_odd_csp()

        setTO(timeout)
        stu_prop.prop_GAC(csp)
        setTO(0)

        curr_vars = csp.get_all_vars()
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[1,2,3,4],[1,2,3,4]]

        if var_domain != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,var_domain)
            details = "Failed GAC test that should have resulted in no pruning"
        else:
            details = ""
            score = 6
    except TO_exc:
        details = "Got a TIMEOUT while testing simple GAC that should result in no pruning"
    except Exception:
        details = "One or more runtime errors occurred while testing simple GAC that should result in no pruning: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(4)
##A problem with 10 queens
def test_gac_10queens(stu_prop):
    score = 4
    #timeout = 1200
    did_fail = False

    try:
        queens = nQueens(10)
        curr_vars = queens.get_all_vars()
        curr_vars[3].assign(8)

        sol_queens = nQueens(10)
        sol_vars = sol_queens.get_all_vars()
        sol_vars[3].assign(8)
        stu_prop.prop_GAC(sol_queens,newVar=sol_vars[3])

        setTO(timeout)
        val, prunes = stu_prop.prop_GAC(queens,newVar=curr_vars[3])
        if not val:
            setTO(0)
            details = "Failed GAC test with 10 queens: expected prop_GAC to return True, but got False"
            #return 0, "FAILED\nNot a DWO. Expected prop_GAC to return True, prunings. prop_GAC returned False"
            return 0, details
        else:
            for i in range(len(curr_vars)):
                if set(curr_vars[i].cur_domain()) != set(sol_vars[i].cur_domain()):
                    curr_vars[i].cur_domain().sort()
                    sol_vars[i].cur_domain().sort()
                    setTO(0)
                    details = "Failed GAC test with 10 queens: variable domains don't match expected results"
                    #return 0, "FAILED\nExpected output: %r\nOutput received: %r" % (curr_vars[i].cur_domain(),sol_vars[i].cur_domain())
                    return 0, details
        setTO(0)
        return score, ""
    except TO_exc:
        details = "Got a TIMEOUT while testing GAC on a 10 queens problem"
    except:
        details = "One or more runtime errors occurred while testing GAC on a 10 queens problem: %r" % traceback.format_exc()

    setTO(0)
    return 0, details

#@max_grade(4)
##A problem with 10 queens
def test_fc_10queens(stu_prop):
    score = 4
    #timeout = 1200
    did_fail = False

    try:
        queens = nQueens(10)
        curr_vars = queens.get_all_vars()
        curr_vars[3].assign(8)

        sol_queens = nQueens(10)
        sol_vars = sol_queens.get_all_vars()
        sol_vars[3].assign(8)
        stu_prop.prop_FC(sol_queens,newVar=sol_vars[3])

        setTO(timeout)
        val, prunes = stu_prop.prop_FC(queens,newVar=curr_vars[3])
        if not val:
            setTO(0)
            details = "Failed FC test with 10 queens: expected prop_FC to return True, but got False"
            #return 0, "FAILED\nNot a DWO. Expected prop_FC to return True, prunings. prop_FC returned False"
            return 0, details
        else:
            for i in range(len(curr_vars)):
                if set(curr_vars[i].cur_domain()) != set(sol_vars[i].cur_domain()):
                    curr_vars[i].cur_domain().sort()
                    sol_vars[i].cur_domain().sort()
                    setTO(0)
                    details = "Failed FC test with 10 queens: variable domains don't match expected results"
                    #return 0, "FAILED\nExpected output: %r\nOutput received: %r" % (curr_vars[i].cur_domain(),sol_vars[i].cur_domain())
                    return 0, details
        setTO(0)
        return score, ""
    except TO_exc:
        details = "Got TIMEOUT while testing FC on a 10 queens problem"
    except:
        details = "One or more runtime errors occurred while testing FC on a 10 queens problem: %r" % traceback.format_exc()

    setTO(0)
    return 0,details

#@max_grade(5)
def test_DWO_GAC(stu_prop):
    score = 5
    failed = False
    details = []
    try:
        queens = nQueens(6)
        cur_var = queens.get_all_vars()
        cur_var[0].assign(2)
        setTO(timeout)
        pruned = stu_prop.prop_GAC(queens,newVar=cur_var[0])
        if not pruned[0]:
            return 0, "Failed a GAC test: returned DWO too early"
        cur_var[1].assign(5)
        answer =  [[2], [5], [], [1], [4], [6]]
        pruned = stu_prop.prop_GAC(queens,newVar=cur_var[1])
        setTO(0)
        if pruned[0]:
            #return 0, "FAILED\nShould result in a DWO.\nExpected variable domains: %r\nVariable domains received: %r" % (answer, [x.cur_domain() for x in cur_var])
            return 0, "Failed a GAC test: should have resulted in a DWO"
        else:
            return score, ""
    except TO_exc:
        details = "Got a TIMEOUT while testing GAC that should have resulted in a DWO"
    except Exception:
        details = "One or more runtime errors occurred while testing GAC that should have resulted in a DWO: %r" % traceback.format_exc()
    setTO(0)
    return 0,details

#@max_grade(5)
def test_DWO_FC(stu_prop):
    score = 5
    failed = False
    details = []

    try:
        queens = nQueens(6)
        cur_var = queens.get_all_vars()
        cur_var[0].assign(2)
        setTO(timeout)
        pruned = stu_prop.prop_FC(queens,newVar=cur_var[0])
        if not pruned[0]:
            setTO(0)
            return 0, "Failed a FC test: returned DWO too early."
        cur_var[1].assign(5)
        answer =  [[2], [5], [], [1,4,6], [1], [3,4,6]]
        pruned = stu_prop.prop_FC(queens,newVar=cur_var[1])
        if not pruned[0]:
            setTO(0)
            return 0, "Failed a FC test: returned DWO too early."
        cur_var[4].assign(1)
        pruned = stu_prop.prop_FC(queens,newVar=cur_var[4])
        if pruned[0]:
            setTO(0)
            #return 0, "FAILED\nShould result in a DWO.\nExpected variable domains: %r\nVariable domains received: %r" % (answer, [x.cur_domain() for x in cur_var])
            return 0, "Failed a FC test: should have resulted in a DWO"
        else:
            setTO(0)
            return score, ""
    except TO_exc:
        details = "Got a TIMEOUT while testing FC that should have resulted in a DWO"
    except Exception:
        details = "One or more runtime errors occurred while testing FC that should have resulted in a DWO: %r" % traceback.format_exc()

    setTO(0)
    return 0,details

##END OF GAC & FC TEST CASES
#################


##############
##OLD MODEL 1 & MODEL 2 TEST CASES

##Checking that importing a board into model 1 works as expected.
##Passing this test is a prereq for passing check_model_1_constraints.
#@max_grade(1)
def model_1_import(stu_models):
    score = 0
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1]]

        setTO(timeout)
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        setTO(0)
        lister = []

        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed to import a board into model 1: initial domains don't match"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while importing board into model 1"
    except Exception:
        details = "One or more runtime errors occurred while importing board into model 1: %r" % traceback.format_exc()

    setTO(0)
    return score,details

##Checking that importing a board into model 2 works as expected.
##Passing this test is a prereq for passing check_model_2_constraints.
#@max_grade(1)
def model_2_import(stu_models):
    score = 0
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1]]

        setTO(timeout)
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        setTO(0)
        lister = []

        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed to import a board into model 2: initial domains don't match"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while importing board into model 2"
    except Exception:
        details = "One or more runtime errors occurred while importing board into model 2: %r" % traceback.format_exc()

    setTO(0)
    return score,details

#@max_grade(1)
def check_model_1_constraints_enum_ineqs(stu_models):
    return 1, ""

#@max_grade(1)
def check_model_2_constraints_enum_ineqs(stu_models):
    return 1, ""

#@max_grade(1)
##Checks that model 1 constraints pass when all different, and fail when not all different
def check_model_1_constraints_enum_rewscols(stu_models):
    score = 1
    details = []
    try:
        # do not use inequalities here
        board = [[3,'.',2,'.',0],[1,'.',3,'.',0],[0,'.',0,'.',0]];

        setTO(timeout)
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        setTO(0)

        for cons in csp.get_all_cons():
            all_vars = cons.get_scope()
            taken = []
            domain_list = []
            should_pass = []
            should_fail = []
            for va in all_vars:
                domain_list.append(va.cur_domain())
                if len(va.cur_domain()) == 1:
                    taken.append(va.cur_domain()[0])
            for i in range(len(all_vars)):
                va = all_vars[i]
                domain = domain_list[i]
                if len(domain) == 1:
                    should_pass.append(domain[0])
                    should_fail.append(domain[0])
                else:
                    for i in range(1,4):
                        if i in domain and i in taken:
                            should_fail.append(i)
                            break
                    for i in range(1,4):
                        if i in domain and i not in taken:
                            should_pass.append(i)
                            taken.append(i)
                            break
                    ##SWITCHING SHOULD PASS AND SHOULD FAIL HERE TO TEST
                    #for i in range(1,4):
                    #    if i in domain and i in taken:
                    #        should_pass.append(i)
                    #        break
                    #for i in range(1,4):
                    #    if i in domain and i not in taken:
                    #        should_fail.append(i)
                    #        taken.append(i)
                    #        break
            if cons.check(should_fail) != cons.check(should_pass):
                if cons.check(should_fail) or not cons.check(should_pass):
                    if not cons.check(should_fail):
                        #details.append("FAILED\nConstraint %s should be falsified by %r" % (str(cons),should_fail))
                        #details.append("var domains:")
                        #for va in all_vars:
                        #    details.append(va.cur_domain())
                        details.append("Failed constraint test in model 1: %s should be falsified by %r" % (str(cons), should_fail))
                    if cons.check(should_pass):
                        #details.append("FAILED\nConstraint %s should be satisfied by %r" % (str(cons),should_pass))
                        #details.append("var domains:")
                        #for va in all_vars:
                        #    details.append(va.cur_domain())
                        details.append("Failed constraint test in model 1: %s should be satisfied by %r" % (str(cons), should_fail))
                    details = "\n".join(details)
                    setTO(0)
                    return 0,details

    except TO_exc:
        details.append("Got a TIMEOUT while testing constraints in model 1")
        details = "\n".join(details)
        setTO(0)
        return 0,details
    except Exception:
        details.append("One or more runtime errors occurred while testing constraints in model 1: %r" % traceback.format_exc())
        details = "\n".join(details)
        setTO(0)
        return 0,details

    details.append("")
    details = "\n".join(details)
    setTO(0)
    return score,details

#@max_grade(1)
##Checks that model 2 constraints pass when all different, and fail when not all different
def check_model_2_constraints_enum_rewscols(stu_models):
    score = 1
    details = []
    try:
        # do not use inequalities here
        board = [[3,'.',2,'.',0],[1,'.',3,'.',0],[0,'.',0,'.',0]];

        setTO(timeout)
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        setTO(0)

        for cons in csp.get_all_cons():
            all_vars = cons.get_scope()
            taken = []
            domain_list = []
            should_pass = []
            should_fail = []
            for va in all_vars:
                domain_list.append(va.cur_domain())
                if len(va.cur_domain()) == 1:
                    taken.append(va.cur_domain()[0])
            for i in range(len(all_vars)):
                va = all_vars[i]
                domain = domain_list[i]
                if len(domain) == 1:
                    should_pass.append(domain[0])
                    should_fail.append(domain[0])
                else:
                    for i in range(1,4):
                        if i in domain and i in taken:
                            should_fail.append(i)
                            break
                    for i in range(1,4):
                        if i in domain and i not in taken:
                            should_pass.append(i)
                            taken.append(i)
                            break
            if cons.check(should_fail) != cons.check(should_pass):
                if cons.check(should_fail) or not cons.check(should_pass):
                    if not cons.check(should_fail):
                        #details.append("FAILED\nConstraint %s should be falsified by %r" % (str(cons),should_fail))
                        #details.append("var domains:")
                        #for va in all_vars:
                        #    details.append(va.cur_domain())
                        details.append("Failed constraint test in model 2: %s should be falsified by %r" % (str(cons), should_fail))
                    if cons.check(should_pass):
                        #details.append("FAILED\nConstraint %s should be satisfied by %r" % (str(cons),should_pass))
                        #details.append("var domains:")
                        #for va in all_vars:
                        #    details.append(va.cur_domain())
                        details.append("Failed constraint test in model 2: %s should be satisfied by %r" % (str(cons), should_fail))
                    details = "\n".join(details)
                    setTO(0)
                    return 0,details

    except TO_exc:
        details.append("Got a TIMEOUT while testing constraints in model 2")
        details = "\n".join(details)
        setTO(0)
        return 0,details
    except Exception:
        details.append("One or more runtime errors occurred while testing constraints in model 2: %r" % traceback.format_exc())
        details = "\n".join(details)
        setTO(0)
        return 0,details

    details.append("")
    details = "\n".join(details)
    setTO(0)
    return score,details


##Checks that model 1 constraints are implemented as expected.
##Both model_1_import must pass and prop_FC must be implemented correctly for this test to behave as intended.
#@max_grade(1)
def check_model_1_constraints_FC(stu_model, stu_prop):
    score = 0
    details = []
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1]]


        setTO(timeout)
        csp, var_array = stu_model.futoshiki_csp_model_1(board)
        setTO(0)
        lister = []
        setTO(timeout)
        stu_prop.prop_FC(csp)
        setTO(0)
        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed FC propagation test on model 1"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing FC on model 1"
    except Exception:
        details = "One or more runtime errors occurred while testing FC on model 1: %r" % traceback.format_exc()

    setTO(0)
    return score,details

##Checks that model 1 constraints are implemented as expected.
##Both model_1_import must pass and prop_GAC must be implemented correctly for this test to behave as intended.
#@max_score(1)
def check_model_1_constraints_GAC(stu_model, soln_propagators):
    score = 0
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 4], [1, 2], [2, 4], [1, 2, 4], [1, 2, 3, 4], [1, 2, 3, 4], [2, 3, 4], [1, 2, 4], [1, 2, 3], [2, 3, 4], [2, 3, 4], [2, 4], [3, 4], [2, 3], [1]]

        setTO(timeout)
        csp, var_array = stu_model.futoshiki_csp_model_1(board)
        setTO(0)
        lister = []
        setTO(timeout)
        soln_propagators.prop_GAC(csp)
        setTO(0)
        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed GAC propagation test on model 1"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing GAC on model 1"
    except Exception:
        details = "One or more runtime errors occurred while testing GAC on model 1: %r" % traceback.format_exc()

    setTO(0)
    return score,details


##Both model_1_import must pass and prop_GAC must be implemented correctly for this test to behave as intended.
#@max_score(1)
def check_model_1_constraints_GAC(stu_model, stu_propagators):
    score = 0
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 4], [1, 2], [2, 4], [1, 2, 4], [1, 2, 3, 4], [1, 2, 3, 4], [2, 3, 4], [1, 2, 4], [1, 2, 3], [2, 3, 4], [2, 3, 4], [2, 4], [3, 4], [2, 3], [1]]

        setTO(timeout)
        csp, var_array = stu_model.futoshiki_csp_model_1(board)
        setTO(0)
        lister = []
        setTO(timeout)
        soln_propagators.prop_GAC(csp)
        setTO(0)
        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed GAC propagation test on model 1"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing GAC on model 1"
    except Exception:
        details = "One or more runtime errors occurred while testing GAC on model 1: %r" % traceback.format_exc()

    setTO(0)
    return score,details

##Checks that model 2 constraints are implemented as expected.
##Both model_2_import must pass and prop_GAC must be implemented correctly for this test to behave as intended.
#@max_grade(1)
def check_model_2_constraints_FC(stu_model, stu_propagators):
    score = 0
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1]]

        setTO(timeout)
        csp, var_array = stu_model.futoshiki_csp_model_2(board)
        setTO(0)
        lister = []
        setTO(timeout)
        stu_propagators.prop_FC(csp)
        setTO(0)
        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed FC propagation test on model 2"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing FC on model 2"
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing FC on model 2: %r" % traceback.format_exc()

    return score,details

##Checks that model 2 constraints are implemented as expected.
##Both model_2_import must pass and prop_GAC must be implemented correctly for this test to behave as intended.
def check_model_2_constraints_GAC(stu_model, soln_propagators):
    score = 0
    try:
        board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]];
        answer = [[3], [1, 2, 4], [1, 2], [2, 4], [1, 2, 4], [1, 2, 3, 4], [1, 2, 3, 4], [2, 3, 4], [1, 2, 4], [1, 2, 3], [2, 3, 4], [2, 3, 4], [2, 4], [3, 4], [2, 3], [1]]

        setTO(timeout)
        csp, var_array = stu_model.futoshiki_csp_model_2(board)
        setTO(0)
        lister = []
        setTO(timeout)
        soln_propagators.prop_GAC(csp)
        setTO(0)
        for i in range(4):
            for j in range(4):
                lister.append(var_array[i][j].cur_domain())

        if lister != answer:
            #details = "FAILED\nExpected Output: %r\nOutput Received: %r" % (answer,lister)
            details = "Failed GAC propagation test on model 2"
        else:
            details = ""
            score = 1
    except TO_exc:
        details = "Got a TIMEOUT while testing GAC on model 2"
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing GAC on model 2: %r" % traceback.format_exc()

    return score,details

#@max_grade(4)
def test_UNSAT_problem_model_1(stu_model):
    score = 4
    try:
        board = [[0,'.',2,'.',1,'.',0,'<',0],[0,'<',0,'.',3,'.',4,'.',0],[0,'<',0,'<',0,'.',2,'.',0],[0,'.',0,'.',0,'.',1,'.',0],[0,'.',0,'<',4,'>',0,'.',2]]

        setTO(timeout)
        csp,var_array = stu_model.futoshiki_csp_model_1(board)
        setTO(0)

        setTO(timeout)
        solver = BT(csp)
        solver.bt_search(soln_propagators.prop_GAC)
        setTO(0)
        for i in range(len(var_array)):
            for j in range(len(var_array)):
                if var_array[i][j].get_assigned_value() is not None:
                    #return 0,"FAILED\n cell [%d][%d] assigned %r; but problem is unsovable" % (i,j,var_array[i][j].get_assigned_value())
                    return 0,"Failed model 1 test: 'solved' unsolvable problem"

        return score, ""

    except TO_exc:
        details = "Got a TIMEOUT while testing model 1 and an unsolvable problem"
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing model 1 and an unsolvable problem: %r" % traceback.format_exc()
    return 0,details

#@max_grade(4)
def test_UNSAT_problem_model_2(stu_model):
    score = 4
    try:
        board = [[0,'.',2,'.',1,'.',0,'<',0],[0,'<',0,'.',3,'.',4,'.',0],[0,'<',0,'<',0,'.',2,'.',0],[0,'.',0,'.',0,'.',1,'.',0],[0,'.',0,'<',4,'>',0,'.',2]]

        setTO(timeout)
        csp,var_array = stu_model.futoshiki_csp_model_2(board)
        setTO(0)

        setTO(timeout)
        solver = BT(csp)
        solver.bt_search(soln_propagators.prop_GAC)
        setTO(0)
        for i in range(len(var_array)):
            for j in range(len(var_array)):
                if var_array[i][j].get_assigned_value() is not None:
                    #return 0,"FAILED\n cell [%d][%d] assigned %r; but problem is unsovable" % (i,j,var_array[i][j].get_assigned_value())
                    return 0,"Failed model 2 test: 'solved' unsolvable problem"

        return score, ""

    except TO_exc:
        details = "Got a TIMEOUT while testing model 2 and an unsolvable problem"
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing model 2 and an unsolvable problem: %r" % traceback.format_exc()
    return 0,details

##Checks that students followed the handout and actually only have constraints over two variables
#@max_grade(2)
def check_binary_constraint_model_1(stu_model):
    score = 2

    try:
        board = [[0,'.',2,'.',0,'.',0,'.',0],[0,'>',3,'.',0,'.',0,'<',0],[2,'.',0,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'<',0,'.',0],[0,'>',0,'.',0,'.',0,'.',5]]

        setTO(timeout)
        csp,var_array = stu_model.futoshiki_csp_model_1(board)

        all_cons = csp.get_all_cons()

        for con in all_cons:
            all_vars = con.get_scope()

            if len(all_vars) != 2:
                setTO(0)
                return 0, "Model 1 specifies ONLY binary constraints. Found a constraint of length %d" % len(all_vars)
        setTO(0)
        return score, ""

    except TO_exc:
        details = "Got a TIMEOUT while testing model 1"
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing model 1: %r" % traceback.format_exc()
    return 0, details

#@max_grade(2)
def check_nary_constraint_model_2(stu_model):
    score = 2

    try:
        board = [[0,'.',2,'.',0,'.',0,'.',0],[0,'>',3,'.',0,'.',0,'<',0],[2,'.',0,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'<',0,'.',0],[0,'>',0,'.',0,'.',0,'.',5]]

        setTO(timeout)
        csp,var_array = stu_model.futoshiki_csp_model_2(board)

        all_cons = csp.get_all_cons()

        saw_nary = False

        for con in all_cons:
            all_vars = con.get_scope()

            if len(all_vars) == 5:
                saw_nary = True
            elif len(all_vars) != 2:
                setTO(0)
                return 0, "Model 2 specifies ONLY binary and nary constraints. Found a constraint of length %d, on a 5x5 board" % len(all_vars)
        setTO(0)
        if saw_nary:
            return score, ""
        else:
            return 0, "Model 2 specifies that nary constraints must be used for the row/col constraints.  Only binary constraints were used."

    except TO_exc:
        details = "Got a TIMEOUT while testing model 2"
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing model 2: %r" % traceback.format_exc()
    return 0, details


#@max_grade(4)
def check_out_of_domain_tuple(prop, name=""):
    score = 4

    try:
        board = [[0,'.',2,'.',0,'.',0,'.',0],[0,'>',3,'.',0,'.',0,'<',0],[2,'.',0,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'<',0,'.',0],[0,'>',0,'.',0,'.',0,'.',5]]

        setTO(timeout)
        csp, var_array = prop(board)

        var_01 = var_array[0][1]

        all_cons = csp.get_cons_with_var(var_01)

        seen_var01 = False
        for con in all_cons:
            curr_scope = con.get_scope()

            if var_01 in curr_scope:
                seen_var01 = True
                if not con.has_support(var_01,2):
                    #setT0(0)
                    return 0, "Failed while testing propagator (%s): a constraint fails on a valid input" % name
                elif con.has_support(var_01,1) or con.has_support(var_01,3) or con.has_support(var_01,4) or con.has_support(var_01,5):
                    #setT0(0)
                    return 0, "Failed while testing propagator (%s): a constraint contains an out-of-domain value" % name

        #setTO(0)
        if seen_var01:
            return score,""
        else:
            #return 0, "FAILED\n, No constraint contained variable in cell 0,1"
            return 0, "Failed while testing propagator (%s): found no constraint containing a specific variable" % name
    except TO_exc:
        details = "Got a TIMEOUT while testing a propagator (%s)" % name
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while testing a propagator (%s): %r" % (name, traceback.format_exc())
    return 0,details

#@max_grade(5)
def test_big_problem(modelfn, prop, name=""):
    score = 5

    try:
        board = [[0,'.',0,'>',8,'.',0,'.',7,'.',0,'.',0,'.',1,'.',0],[0,'.',2,'.',6,'.',4,'.',3,'.',0,'.',8,'.',9,'.',5],[0,'.',0,'.',0,'.',9,'.',1,'.',5,'<',7,'.',0,'.',6],[0,'>',7,'.',1,'.',6,'.',9,'.',4,'.',2,'<',0,'.',0],[0,'>',5,'.',0,'.',0,'.',4,'.',6,'.',3,'.',8,'.',0],[7,'.',3,'.',0,'.',1,'.',0,'.',2,'.',0,'.',6,'.',0],[5,'.',0,'.',0,'.',2,'.',0,'.',8,'.',0,'.',0,'.',9],[6,'.',4,'.',0,'.',3,'<',0,'.',0,'.',1,'.',0,'<',8],[0,'<',6,'>',5,'.',8,'.',0,'>',0,'.',0,'.',0,'<',0]]

        setTO(timeout)
        csp,var_array = modelfn(board)

        answer = [[4], [9], [8], [5], [7], [3], [6], [1], [2], [1], [2], [6], [4], [3], [7], [8], [9], [5], [2], [8], [4], [9], [1], [5], [7], [3], [6], [8], [7], [1], [6], [9], [4], [2], [5], [3], [9], [5], [2], [7], [4], [6], [3], [8], [1], [7], [3], [9], [1], [8], [2], [5], [6], [4], [5], [1], [3], [2], [6], [8], [4], [7], [9], [6], [4], [7], [3], [5], [9], [1], [2], [8], [3], [6], [5], [8], [2], [1], [9], [4], [7]]
        prop.prop_GAC(csp)

        lister = []

        for i in range(9):
            for j in range(9):
                lister.append(var_array[i][j].cur_domain())

        setTO(0)
        if lister == answer:
            return score, ""
        else:
            #return 0,"FAILED\nExplanation:\nvariable domains should be: %r\nvariable domains are: %r" % (answer,lister)
            return 0, "Failed on a large problem using %s" % name

    except TO_exc:
        details = "Got a TIMEOUT on a large problem while using %s" % name
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while using %s on a large problem: %r" % (name, traceback.format_exc())

    return 0,details

#@max_grade(5)
def test_full_run(model,stu_prop,name=""):
    score = 0
    try:
        board = [[0,'>',0,'.',0,'.',0,'.',0,'.',5,'>',0],[6,'.',4,'.',0,'.',0,'>',3,'.',7,'.',0],[0,'<',2,'.',0,'<',0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',4,'.',0,'.',0,'.',0],[0,'.',0,'<',5,'.',0,'.',4,'.',1,'.',0],[0,'.',0,'.',0,'.',0,'.',6,'.',2,'<',3],[4,'<',0,'.',0,'.',7,'.',2,'<',0,'.',5]]

        setTO(timeout)        
        csp,var_array = model(board)

        greater_thans = [(var_array[0][0],var_array[0][1]),(var_array[0][5],var_array[0][6]),(var_array[1][3],var_array[1][4])]
        less_thans = [(var_array[2][0],var_array[2][1]),(var_array[2][2],var_array[2][3]),(var_array[3][1],var_array[3][2]),(var_array[4][1],var_array[4][2]),(var_array[5][5],var_array[5][6]),(var_array[6][0],var_array[6][1]),(var_array[6][4],var_array[6][5])]


        solver = BT(csp)
        solver.bt_search(stu_prop.prop_GAC)
        setTO(0)
        if check_solution(var_array,greater_thans,less_thans):
            score = 5
            details = ""
        else:
            details = "Solution found in full run with GAC on %s was not a valid Futoshiki solution." % name
    except TO_exc:
        details = "Got a TIMEOUT while trying a full run using GAC on %s" % name
    except Exception:
        setTO(0)
        details = "One or more runtime errors occurred while trying a full run using GAC on %s: %r" % (name, traceback.format_exc())

    if score < 5:
        try:
            board = [[0,'>',0,'.',0,'.',0,'.',0,'.',5,'>',0],[6,'.',4,'.',0,'.',0,'>',3,'.',7,'.',0],[0,'<',2,'.',0,'<',0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',4,'.',0,'.',0,'.',0],[0,'.',0,'<',5,'.',0,'.',4,'.',1,'.',0],[0,'.',0,'.',0,'.',0,'.',6,'.',2,'<',3],[4,'<',0,'.',0,'.',7,'.',2,'<',0,'.',5]]

            setTO(timeout)
            csp,var_array = model(board)

            greater_thans = [(var_array[0][0],var_array[0][1]),(var_array[0][5],var_array[0][6]),(var_array[1][3],var_array[1][4])]
            less_thans = [(var_array[2][0],var_array[2][1]),(var_array[2][2],var_array[2][3]),(var_array[3][1],var_array[3][2]),(var_array[4][1],var_array[4][2]),(var_array[5][5],var_array[5][6]),(var_array[6][0],var_array[6][1]),(var_array[6][4],var_array[6][5])]


            solver = BT(csp)
            solver.bt_search(stu_prop.prop_FC)
            setTO(0)
            if check_solution(var_array,greater_thans,less_thans):
                score = 5
                details = ""
            else:
                details = "Solution found in full run with FC on %s was not a valid Futoshiki solution." % name
        except TO_exc:
            details = "Got a TIMEOUT while trying a full run using FC on %s" % name
        except Exception:
            setTO(0)
            details = "One or more runtime errors occurred while trying a full run using FC on %s: %r" % (name, traceback.format_exc())

    return score,details



##RUN TEST CASES (For Joanna)
def main(name, stu_propagators=None, stu_models=None):
    TOTAL_POINTS = 100
    total_score = 0


    if stu_propagators == None:
        import propagators as stu_propagators
    if stu_models == None:
        import futoshiki_csp as stu_models


    scores = []
    print("---starting test_simple_FC---")
    score,details = test_simple_FC(stu_propagators)
    scores.append(score)
    total_score += score
    print("score: %d" % score)
    print(details)
    print("---finished test_simple_FC---\n")

    print("---starting test_simple_GAC---")
    score,details = test_simple_GAC(stu_propagators)
    scores.append(score)
    total_score += score
    print("score: %d" % score)
    print(details)
    print("---finished test_simple_GAC---\n")

    print("---starting three_queen_FC---")
    score,details = three_queen_FC(stu_propagators)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---finished three_queen_FC---\n")

    print("---starting three_queen_GAC---")
    score,details = three_queen_GAC(stu_propagators)
    scores.append(score)
    total_score+=score
    print(details)
    print("score: %d" % score)
    print("---finished three_queen_GAC---\n")

    print("---begin test_1 fc---")
    score,details = test_1(stu_propagators.prop_FC)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_1 fc---\n")

    print("---begin test_1 gac---")
    score,details = test_1(stu_propagators.prop_GAC)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_1 gac---\n")

    print("---begin test_2 fc---")
    score,details = test_2(stu_propagators.prop_FC)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_2 fc---\n")

    print("---begin test_2 gac---")
    score,details = test_2(stu_propagators.prop_GAC)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_2 gac---\n")

    print("---begin test_3 fc---")
    score,details = test_3(stu_propagators.prop_FC)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_3 fc---\n")

    print("---begin test_3 gac---")
    score,details = test_3(stu_propagators.prop_GAC)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_3 gac---\n")

    ##NEW STUFF

    print("---begin test_tiny_adder_FC---")
    score,details = test_tiny_adder_FC(stu_propagators)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_tiny_adder_FC---\n")

    print("---begin test_tiny_adder_GAC---")
    score,details = test_tiny_adder_GAC(stu_propagators)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_tiny_adder_GAC---\n")

    print("---begin test_no_pruning_FC---")
    score,details = test_no_pruning_FC(stu_propagators)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_no_pruning_FC---\n")

    print("---begin test_no_pruning2_FC---")
    score,details = test_no_pruning2_FC(stu_propagators)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_no_pruning2_FC---\n")

    print("---begin test_no_pruning_GAC---")
    score,details = test_no_pruning_GAC(stu_propagators)
    scores.append(score)
    total_score += score
    print(details)
    print("score: %d" % score)
    print("---end test_no_pruning_GAC---\n")

    print("---starting test_gac_10queens---")
    score, details = test_gac_10queens(stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_gac_10queens---\n")

    print("---starting test_fc_10queens---")
    score, details = test_fc_10queens(stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_fc_10queens---\n")

    print("---starting test_DWO_GAC---")
    score,details = test_DWO_GAC(stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_DWO_GAC---")

    print("---starting test_DWO_FC---\n")
    score,details = test_DWO_FC(stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_DWO_FC---\n")

    print("---STARTING MODEL TESTS---\n")

    print("---starting model_1_import---")
    score,details = model_1_import(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished model_1_import---\n")

    print("---starting model_2_import---")
    score,details = model_2_import(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished model_2_import---\n")

    print("---starting check_model_1_constraints_enum_rewscols---")
    score,details = check_model_1_constraints_enum_rewscols(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_1_constraints_enum_rewscols---\n")

    print("---starting check_model_1_constraints_enum_ineqs---")
    score,details = check_model_1_constraints_enum_ineqs(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_1_constraints_enum_ineqs---")

    print("---starting check_model_2_constraints_enum_ineqs---")
    score,details = check_model_2_constraints_enum_ineqs(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_2_constraints_enum_ineqs---")

    print("---starting check_model_2_constraints_enum_rewscols---")
    score,details = check_model_2_constraints_enum_rewscols(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_2_constraints_enum_rewscols---\n")

    print("---starting check_model_1_constraints_FC---")
    score,details = check_model_1_constraints_FC(stu_models, stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_1_constraints_FC---")

    print("---starting check_model_2_constraints_FC---")
    score,details = check_model_2_constraints_FC(stu_models, stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_2_constraints_FC---")

    print("---starting check_model_1_constraints_GAC---")
    score,details = check_model_1_constraints_GAC(stu_models, stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_1_constraints_GAC---")

    print("---starting check_model_2_constraints_GAC---")
    score,details = check_model_2_constraints_GAC(stu_models, stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_model_2_constraints_GAC---")

    print("---starting unsolvable model 1---")
    score,details = test_UNSAT_problem_model_1(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished unsolvable model 1---\n")

    print("---starting unsolvable model 2---")
    score,details = test_UNSAT_problem_model_2(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished unsolvable model 2---\n")

    print("---starting binary model 1---")
    score,details = check_binary_constraint_model_1(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished binary model 1---\n")

    print("---starting nary model 2---")
    score,details = check_nary_constraint_model_2(stu_models)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished nary model 2---\n")

    print("---starting check_out_of_domain_tuple_model_1---")
    score,details = check_out_of_domain_tuple(stu_models.futoshiki_csp_model_1)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_out_of_domain_tuple_model_1---\n")

    print("---starting check_out_of_domain_tuple_model_2---")
    score,details = check_out_of_domain_tuple(stu_models.futoshiki_csp_model_2)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished check_out_of_domain_tuple_model_2---\n")


    print("---starting test_big_problem_model1---")
    score,details = test_big_problem(stu_models.futoshiki_csp_model_1, stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_big_problem_model1---\n")

    print("---starting test_big_problem_model2---")
    score,details = test_big_problem(stu_models.futoshiki_csp_model_2, stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_big_problem_model2---\n")

    print("---starting test_full_run_model1---")
    score,details = test_full_run(stu_models.futoshiki_csp_model_1,stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_full_run_model1---\n")

    print("---starting test_full_run_model2---")
    score,details = test_full_run(stu_models.futoshiki_csp_model_2,stu_propagators)
    scores.append(score)
    print(details)
    print("score: %d" % score)
    total_score += score
    print("---finished test_full_run_model2---\n")

    if total_score == TOTAL_POINTS:
        print("Score: %d/%d; Passed all tests" % (total_score,TOTAL_POINTS))
    else:
        print("Score: %d/%d; Did not pass all tests." % (total_score,TOTAL_POINTS))


    f = open("../../scores.txt", "a")
    resultString = ','.join(map(str, scores))
    f.write(name + "," + resultString + "," + str(total_score) +"\n")
    f.close()


if __name__=="__main__":
    main(sys.argv[1])
