import sys
import itertools
import traceback
import statistics
import pickle
import os

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM
from utils.test_tools import max_grade
from .test_cases_helpers import *
from dependencies.csp import *
from dependencies.class_scheduling import *

STUDENT_CSP = 'csp_problems.py'
CONSTRAINTS = 'constraints.py'
BT_CODE = 'backtracking.py'
LOCATION_PREFIX = './student_grader/assignment'
DEFAULT_TIMEOUT = 20
timeout = 60


# QUESTION 1 ====================================================
@max_grade(2)
def test_question_1_test_1(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)
        q2 = Variable("Q2", [1, 2, 3, 4, 5])
        q5 = Variable("Q5", [1, 2, 3, 4, 5])
        c  = stu_all.QueensTableConstraint("Q2/Q5", q2, q5, 2, 5)
        setTO(0)
        q2.setValue(2)
        for val in q5.domain():
            q5.setValue(val)
            if c.check():
                if val in [2,5]:
                    details = "Queens table constraint check routine failed. Q2={}, Q5={} not detected as falsifying constraint".format(q2.getValue(), q5.getValue())
                    did_fail = True
            else:
                if val in [1,3,4]:
                    details = "Queens table constraint check routine failed. Q2={}, Q5={} not detected as falsifying constraint".format(q2.getValue(), q5.getValue())
                    did_fail = True

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing Queens Table Constraint"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing Queens Table Constraint: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(2)
def test_question_1_test_2(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)
        
        q2 = Variable("Q2", [1, 2, 3, 4, 5])
        q5 = Variable("Q5", [1, 2, 3, 4, 5])
        q3 = Variable("Q3", [1, 2, 3, 4, 5])
        q2.pruneValue(1, None, None)
        q2.pruneValue(4, None, None)
        q2.pruneValue(5, None, None)
        c = stu_all.QueensTableConstraint("Q2/Q5", q2, q3, 2, 3)

        setTO(0)
        
        for val in q3.domain():
            if c.hasSupport(q3, val):
                if val not in [1, 4, 5]:
                    details = "Queens table constraint hasSupport routine failed. Q2 current domain = {}, Q3 = {} detected to have support (doesn't)".format(q2.curDomain(), val)
                    did_fail = True
            else:
                if val not in [2, 3]:
                    details = "Queens table constraint hasSupport routine failed. Q2 current domain = {}, Q3 = {} detected to not have support (does)".format(q2.curDomain(), val)
                    did_fail = True
    
        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing Queens Table Constraint"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing Queens Table Constraint: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(3)
def test_question_1_test_3(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)
        
        csp = stu_all.nQueens(8, 'table')
        solutions, num_nodes = stu_all.bt_search('BT', csp, 'fixed', True, False)

        setTO(0)
        
        if num_nodes != 1965:
            details = "Queens table constraint not working correctly. BT should explore 1965 nodes. With your implementation it explores {}".format(num_nodes)
            did_fail = True
        if len(solutions) != 92:
            details = "Queens table constraint not working correctly. BT should return 92 solutions. With your implementation it returns {}".format(len(solutions))
            did_fail = True
    
        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing Queens Table Constraint"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing Queens Table Constraint: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(3)
def test_question_1_test_4(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)
        
        csp = stu_all.nQueens(3, 'table')
        solutions, num_nodes = stu_all.bt_search('BT', csp, 'fixed', True, False)

        setTO(0)
        
        if num_nodes != 6:
            details = "Queens table constraint not working correctly. BT should explore 6 nodes. With your implementation it explores {}".format(num_nodes)
            did_fail = True
        if len(solutions) != 0:
            details = "Queens table constraint not working correctly. BT should return 0 solutions. With your implementation it returns {}".format(len(solutions))
            did_fail = True
    
        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing Queens Table Constraint"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing Queens Table Constraint: %r" % traceback.format_exc()

    setTO(0)

    return score,details


# QUESTION 2 ====================================================
@max_grade(4)
def test_question_2_test_1(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    score = 0

    did_fail = False
    try:
        setTO(timeout)
        queens = stu_all.nQueens(8, 'row')
        solutions, _ = stu_all.bt_search('FC', queens, 'mrv', False, False)

        setTO(0)
        errors = queens.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Failed simple FC test: Invalid solution returned by FC"

        if len(solutions) != 1:
            did_fail = True
            details = "Failed simple FC test: FC failed to return only one solution"

        for v in queens.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                print("Failed simple FC test: FC failed to restore domains of variables")
                break

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing FC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing FC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


@max_grade(4)
def test_question_2_test_2(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    score = 0

    did_fail = False
    try:
        setTO(timeout)
        queens = stu_all.nQueens(8, 'row')
        
        solutions, _ = stu_all.bt_search('FC', queens, 'mrv', True, False)

        setTO(0)
        errors = queens.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Failed simple FC test: Invalid solution(s) returned by FC"

        if len(solutions) != 92:
            did_fail = True
            details = "Failed simple FC test: FC failed to return 92 solutions"

        for v in queens.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                print("Failed simple FC test: FC failed to restore domains of variables")
                break

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing FC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing FC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


@max_grade(4)
def test_question_2_test_3(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    score = 0

    did_fail = False
    try:
        setTO(timeout)
        queens = stu_all.nQueens(3, 'row')
        
        solutions, _ = stu_all.bt_search('FC', queens, 'mrv', True, False)

        setTO(0)
        errors = queens.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Failed simple FC test: Invalid solution(s) returned by FC"

        if len(solutions) != 0:
            did_fail = True
            details = "Failed simple FC test: FC failed to return 0 solution"

        for v in queens.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                print("Failed simple FC test: FC failed to restore domains of variables")
                break

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing FC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing FC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


@max_grade(4)
def test_question_2_test_4(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    score = 0

    did_fail = False
    try:
        setTO(timeout)
        queens = stu_all.nQueens(20, 'row')
        solutions, _ = stu_all.bt_search('FC', queens, 'fixed', False, False)

        setTO(0)
        errors = queens.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Failed simple FC test: Invalid solution returned by FC"

        if len(solutions) != 1:
            did_fail = True
            details = "Failed simple FC test: FC failed to return only one solution"

        for v in queens.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                print("Failed simple FC test: FC failed to restore domains of variables")
                break

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing FC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing FC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


@max_grade(4)
def test_question_2_test_5(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    score = 0

    did_fail = False
    try:
        setTO(timeout)
        queens = stu_all.nQueens(12, 'row')
        solutions, _ = stu_all.bt_search('FC', queens, 'fixed', True, False)

        setTO(0)
        errors = queens.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Failed simple FC test: Invalid solution returned by FC"

        if len(solutions) != 14200:
            did_fail = True
            details = "Failed simple FC test: FC failed to return 14200 solutions"

        for v in queens.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                print("Failed simple FC test: FC failed to restore domains of variables")
                break

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing FC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing FC: %r" % traceback.format_exc()

    setTO(0)
    return score,details


# QUESTION 3 ====================================================
@max_grade(2)
def test_question_3_test_1(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 2])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        v6 = Variable('V6', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v7 = Variable('V7', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v8 = Variable('V8', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v9 = Variable('V9', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        vars = [v1, v2, v3, v4, v5, v6, v7, v8, v9]
        ac = stu_all.AllDiffConstraint('test9', vars)
        testcsp = CSP('test', vars, [ac])
        stu_all.GacEnforce([ac], testcsp, None, None)


        test1 = "    v1 = Variable('V1', [1, 2])\n\
        v2 = Variable('V2', [1, 2])\n\
        v3 = Variable('V3', [1, 2, 3, 4, 5])\n\
        v4 = Variable('V4', [1, 2, 3, 4, 5])\n\
        v5 = Variable('V5', [1, 2, 3, 4, 5])\n\
        v6 = Variable('V6', [1, 2, 3, 4, 5, 6, 7, 8, 9])\n\
        v7 = Variable('V7', [1, 2, 3, 4, 5, 6, 7, 8, 9])\n\
        v8 = Variable('V8', [1, 2, 3, 4, 5, 6, 7, 8, 9])\n\
        v9 = Variable('V9', [1, 2, 3, 4, 5, 6, 7, 8, 9])\n\
        vars = [v1, v2, v3, v4, v5, v6, v7, v8, v9]\n\
        ac = AllDiffConstraint('test9', vars)\n\
        testcsp = CSP('test', vars, [ac])\n\
        GacEnforce([ac], testcsp, None, None)"

        soln_doms = [ set([1,2]), set([1,2]), set([3,4,5]), set([3,4,5]), set([3,4,5]),
                      set([6, 7, 8, 9]), set([6, 7, 8, 9]), set([6, 7, 8, 9]), set([6, 7, 8, 9]) ]

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC Enforce"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing GAC Enforce: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(3)
def test_question_3_test_2(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 2])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        v6 = Variable('V6', [1, 3, 4, 5])
        v7 = Variable('V7', [1, 3, 4, 5])
        ac1 = stu_all.AllDiffConstraint('1', [v1,v2,v3])
        ac2 = stu_all.AllDiffConstraint('1', [v1,v2,v4])
        ac3 = stu_all.AllDiffConstraint('1', [v1,v2,v5])
        ac4 = stu_all.AllDiffConstraint('1', [v3,v4,v5,v6])
        ac5 = stu_all.AllDiffConstraint('1', [v3,v4,v5,v7])
        vars = [v1, v2, v3, v4, v5, v6, v7]
        cnstrs = [ac1,ac2,ac3,ac4,ac5]
        testcsp = CSP('test2', vars, cnstrs)
        stu_all.GacEnforce(cnstrs, testcsp, None, None)

        test2 = "    v1 = Variable('V1', [1, 2])\n\
        v2 = Variable('V2', [1, 2])\n\
        v3 = Variable('V3', [1, 2, 3, 4, 5])\n\
        v4 = Variable('V4', [1, 2, 3, 4, 5])\n\
        v5 = Variable('V5', [1, 2, 3, 4, 5])\n\
        v6 = Variable('V6', [1, 3, 4, 5])\n\
        v7 = Variable('V7', [1, 3, 4, 5])\n\
        ac1 = AllDiffConstraint('1', [v1,v2,v3])\n\
        ac2 = AllDiffConstraint('1', [v1,v2,v4])\n\
        ac3 = AllDiffConstraint('1', [v1,v2,v5])\n\
        ac4 = AllDiffConstraint('1', [v3,v4,v5,v6])\n\
        ac5 = AllDiffConstraint('1', [v3,v4,v5,v7])\n\
        vars = [v1, v2, v3, v4, v5, v6, v7]\n\
        cnstrs = [ac1,ac2,ac3,ac4,ac5]\n\
        testcsp = CSP('test2', vars, cnstrs)\n\
        GacEnforce(cnstrs, testcsp, None, None)"

        soln_doms = [ set([1,2]), set([1,2]), set([3, 4, 5]), set([3,4,5]), set([3,4,5]),
                      set([1]), set([1]) ]

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))
       
        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC Enforce"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing GAC Enforce: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(3)
def test_question_3_test_3(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 2])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        v6 = Variable('V6', [1, 3, 4, 5])
        v7 = Variable('V7', [1, 3, 4, 5])    
        ac1 = stu_all.AllDiffConstraint('1', [v1,v2,v3,v4,v5,v6,v7])
        vars = [v1, v2, v3, v4, v5, v6, v7]
        cnstrs = [ac1]
        testcsp = CSP('test2', vars, cnstrs)
        val = stu_all.GacEnforce(cnstrs, testcsp, None, None)

        test3 = "    v1 = Variable('V1', [1, 2])\n\
        v2 = Variable('V2', [1, 2])\n\
        v3 = Variable('V3', [1, 2, 3, 4, 5])\n\
        v4 = Variable('V4', [1, 2, 3, 4, 5])\n\
        v5 = Variable('V5', [1, 2, 3, 4, 5])\n\
        v6 = Variable('V6', [1, 3, 4, 5])\n\
        v7 = Variable('V7', [1, 3, 4, 5])\n\
        ac1 = AllDiffConstraint('1', [v1,v2,v3,v4,v5,v6,v7])\n\
        vars = [v1, v2, v3, v4, v5, v6, v7]\n\
        cnstrs = [ac1]\n\
        testcsp = CSP('test2', vars, cnstrs)\n\
        val = GacEnforce(cnstrs, testcsp, None, None)"

        if val != "DWO":
            did_fail = True
            details = "Error: GacEnforce failed to return \"DWO\" returned {} instead".format(val)
        
        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC Enforce"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing GAC Enforce: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(4)
def test_question_3_test_4(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False

    try:
        setTO(timeout)

        csp = stu_all.nQueens(8, 'row')
        solutions, num_nodes = stu_all.bt_search('GAC', csp, 'fixed', False, False)
        errors = csp.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Fail Q3 test 4: invalid solution(s) returned by GAC"

        if len(solutions) != 1:
            did_fail = True
            details = "Fail Q3 test 4: GAC failed to return only one solution"
    
        ok=True
        for v in csp.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                details = "Fail Q3 test 4: GAC failed to restore domains of variables"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing GAC: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(4)
def test_question_3_test_5(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False

    try:
        setTO(timeout)

        csp = stu_all.nQueens(10, 'row')
        solutions, num_nodes = stu_all.bt_search('GAC', csp, 'fixed', True, False)
        errors = csp.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Fail Q3 test 5: invalid solution(s) returned by GAC"

        if len(solutions) != 724:
            did_fail = True
            details = "Fail Q3 test 5: GAC failed to return 724 solutions"
            
        ok=True
        for v in csp.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                details = "Fail Q3 test 5: GAC failed to restore domains of variables"
                break
        
        setTO(0)

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing GAC: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(4)
def test_question_3_test_6(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False

    try:
        setTO(timeout)

        csp = stu_all.nQueens(15, 'row')
        solutions, num_nodes = stu_all.bt_search('GAC', csp, 'fixed', False, False)
        errors = csp.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Fail Q3 test 6: invalid solution(s) returned by GAC"

        if len(solutions) != 1:
            did_fail = True
            details = "Fail Q3 test 6: GAC failed to return one solution"
            
        ok=True
        for v in csp.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                details = "Fail Q3 test 6: GAC failed to restore domains of variables"
                break
        
        setTO(0)

        if not did_fail:
            details = ""
            score = 4

    except TO_exc:
        details = "Got a TIMEOUT while testing GAC"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing GAC: %r" % traceback.format_exc()

    setTO(0)

    return score,details


# QUESTION 4 ====================================================
@max_grade(2)
def test_question_4_test_1(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        csp = stu_all.nQueens(6, 'alldiff')
        solutions, num_nodes = stu_all.bt_search('BT', csp, 'fixed', True, False)
        errors = csp.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Fail Q4 test 1: invalid solution(s) returned by alldiff BT"

        if len(solutions) != 4:
            did_fail = True
            details = "Fail Q4 test 1: alldiff BT failed to return 4 solutions"

        ok=True
        for v in csp.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                details = "Fail Q4 test 1: alldiff BT failed to restore domains of variables"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing alldiff BT"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing alldiff BT: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(2)
def test_question_4_test_2(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        csp = stu_all.nQueens(8, 'alldiff')
        solutions, num_nodes = stu_all.bt_search('BT', csp, 'mrv', True, False)
        errors = csp.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Fail Q4 test 2: invalid solution(s) returned by alldiff BT"

        if len(solutions) != 92:
            did_fail = True
            details = "Fail Q4 test 2: alldiff BT failed to return 92 solutions"

        ok=True
        for v in csp.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                details = "Fail Q4 test 1: alldiff BT failed to restore domains of variables"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing alldiff BT"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing alldiff BT: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(1)
def test_question_4_test_3(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        csp = stu_all.nQueens(10, 'alldiff')
        solutions, num_nodes = stu_all.bt_search('BT', csp, 'mrv', False, False)
        errors = csp.check(solutions)

        if len(errors) > 0:
            did_fail = True
            details = "Fail Q4 test 3: invalid solution(s) returned by alldiff BT"

        if len(solutions) != 1:
            did_fail = True
            details = "Fail Q4 test 3: alldiff BT failed to return one solution"

        ok=True
        for v in csp.variables():
            if set(v.curDomain()) != set(v.domain()):
                did_fail = True
                details = "Fail Q4 test 3: alldiff BT failed to restore domains of variables"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 1

    except TO_exc:
        details = "Got a TIMEOUT while testing alldiff BT"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing alldiff BT: %r" % traceback.format_exc()

    setTO(0)

    return score,details


# QUESTION 5 ====================================================
@max_grade(2)
def test_question_5_test_1(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 2])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        v6 = Variable('V6', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v7 = Variable('V7', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v8 = Variable('V8', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v9 = Variable('V9', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        vars = [v1, v2, v3, v4, v5, v6, v7, v8, v9]
        nv9 = stu_all.NValuesConstraint('9', vars, [9], 4, 5)
        testcsp = CSP('test', vars, [nv9])
        stu_all.GacEnforce([nv9], testcsp, None, None)

        setTO(0)

        soln_doms = [set([1, 2]), set([1, 2]), set([1, 2, 3, 4, 5]),
                     set([1, 2, 3, 4, 5]), set([1, 2, 3, 4, 5]), set([9]),
                     set([9]), set([9]), set([9])]

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))
                break
        
        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing NValues"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing NValues: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(2)
def test_question_5_test_2(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 2])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        v6 = Variable('V6', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v7 = Variable('V7', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v8 = Variable('V8', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v9 = Variable('V9', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        vars = [v1, v2, v3, v4, v5, v6, v7, v8, v9]
        nv9 = stu_all.NValuesConstraint('9', vars, [9], 4, 5)
        nv1 = stu_all.NValuesConstraint('1', vars, [1], 5, 5)
        testcsp = CSP('test', vars, [nv1, nv9])
        stu_all.GacEnforce([nv1, nv9], testcsp, None, None)
        soln_doms = [set([1]), set([1]), set([1]), set([1]), set([1]),
                     set([9]), set([9]), set([9]), set([9])]

        setTO(0)

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))
                break

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing NValue"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing NValues: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(2)
def test_question_5_test_3(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 2])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        v6 = Variable('V6', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v7 = Variable('V7', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v8 = Variable('V8', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        v9 = Variable('V9', [1, 2, 3, 4, 5, 6, 7, 8, 9])
        vars = [v1, v2, v3, v4, v5, v6, v7, v8, v9]
        nv9 = stu_all.NValuesConstraint('9', vars, [8, 9], 4, 5)
        nv1 = stu_all.NValuesConstraint('1', vars, [1], 5, 5)
        testcsp = CSP('test', vars, [nv1, nv9])
        stu_all.GacEnforce([nv1, nv9], testcsp, None, None)
        soln_doms = [set([1]), set([1]), set([1]), set([1]), set([1]),
                     set([8, 9]), set([8, 9]), set([8, 9]), set([8, 9])]

        setTO(0)

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))
                break

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing NValue"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing NValues: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(2)
def test_question_5_test_4(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 3])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2, 3, 4, 5])
        v4 = Variable('V4', [1, 2, 3, 4, 5])
        v5 = Variable('V5', [1, 2, 3, 4, 5])
        vars = [v1, v2, v3, v4, v5]
        nv2 = stu_all.NValuesConstraint('2', vars, [2], 4, 4)
        nv3 = stu_all.NValuesConstraint('3', vars, [3], 1, 4)
        testcsp = CSP('test', vars, [nv2, nv3])
        stu_all.GacEnforce([nv2, nv3], testcsp, None, None)
        soln_doms = [set([3]), set([2]), set([2]), set([2]), set([2])]

        setTO(0)

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))
                break

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing NValue"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing NValues: %r" % traceback.format_exc()

    setTO(0)

    return score,details


@max_grade(2)
def test_question_5_test_5(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]
    
    score = 0
    did_fail = False

    try:
        setTO(timeout)

        v1 = Variable('V1', [1, 3])
        v2 = Variable('V2', [1, 2])
        v3 = Variable('V3', [1, 2])
        v4 = Variable('V4', [1, 2])
        vars = [v1, v2, v3, v4]
        nv2 = stu_all.NValuesConstraint('2_3', vars, [2, 3], 4, 4)
        testcsp = CSP('test', vars, [nv2])
        stu_all.GacEnforce([nv2], testcsp, None, None)
        soln_doms = [set([3]), set([2]), set([2]), set([2])]

        setTO(0)

        for i, v in enumerate(vars):
            if set(v.curDomain()) != soln_doms[i]:
                did_fail = True
                details = "Error: {}.curDomain() == {}. Correct curDomin should be == {}".format(v.name(), v.curDomain(), list(soln_doms[i]))
                break

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing NValue"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing NValues: %r" % traceback.format_exc()

    setTO(0)

    return score,details


# QUESTION 6 ====================================================
@max_grade(2)
def test_question_6_test_1(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        solutions = stu_all.solve_schedules(c1, 'BT', True, 'mrv', True, False)

        if len(solutions) != 1:
            did_fail = True
            details = "Fail Q6 test 1: class scheduling failed to return one solution"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(c1, s):
                did_fail = True
                details = "Fail Q6 test 1: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(2)
def test_question_6_test_2(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        solutions = stu_all.solve_schedules(c2, 'BT', True, 'mrv', True, False)

        if len(solutions) != 0:
            did_fail = True
            details = "Fail Q6 test 2: class scheduling failed to return no solution"

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(2)
def test_question_6_test_3(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        solutions = stu_all.solve_schedules(c3, 'BT', True, 'mrv', True, False)

        if len(solutions) != 0:
            did_fail = True
            details = "Fail Q6 test 3: class scheduling failed to return no solution"

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(2)
def test_question_6_test_4(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        solutions = stu_all.solve_schedules(c4, 'BT', True, 'mrv', True, False)

        if len(solutions) != 0:
            did_fail = True
            details = "Fail Q6 test 4: class scheduling failed to return no solution"

        setTO(0)

        if not did_fail:
            details = ""
            score = 2

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(3)
def test_question_6_test_5(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        solutions = stu_all.solve_schedules(c5, 'BT', True, 'mrv', True, False)

        if len(solutions) != 2:
            did_fail = True
            details = "Fail Q6 test 5: class scheduling failed to return two solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(c5, s):
                did_fail = True
                details = "Fail Q6 test 5: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(3)
def test_question_6_test_6(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    try:
        setTO(timeout)

        solutions = stu_all.solve_schedules(c6, 'BT', True, 'mrv', True, False)

        if len(solutions) != 6:
            did_fail = True
            details = "Fail Q6 test 6: class scheduling failed to return six solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(c6, s):
                did_fail = True
                details = "Fail Q6 test 6: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details
    

@max_grade(3)
def test_question_6_test_7(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_4.pkl".format(LOCATION_PREFIX)
    
    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 2:
            did_fail = True
            details = "Fail Q6 test 7: class scheduling failed to return two solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 7: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(3)
def test_question_6_test_8(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_1.pkl".format(LOCATION_PREFIX)

    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 2:
            did_fail = True
            details = "Fail Q6 test 8: class scheduling failed to return two solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 8: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(3)
def test_question_6_test_9(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_2.pkl".format(LOCATION_PREFIX)

    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 8:
            did_fail = True
            details = "Fail Q6 test 9: class scheduling failed to return eight solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 9: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details


@max_grade(3)
def test_question_6_test_10(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_3.pkl".format(LOCATION_PREFIX)

    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 9:
            did_fail = True
            details = "Fail Q6 test 10: class scheduling failed to return nine solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 10: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details
    

@max_grade(3)
def test_question_6_test_11(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_5.pkl".format(LOCATION_PREFIX)

    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 6:
            did_fail = True
            details = "Fail Q6 test 11: class scheduling failed to return six solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 11: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details
    

@max_grade(3)
def test_question_6_test_12(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_6.pkl".format(LOCATION_PREFIX)

    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 6:
            did_fail = True
            details = "Fail Q6 test 12: class scheduling failed to return six solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 12: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details
    

@max_grade(3)
def test_question_6_test_13(modules):
    stu_propagators = modules[BT_CODE]
    stu_csp = modules[STUDENT_CSP]
    stu_const = modules[CONSTRAINTS]

    score = 0
    did_fail = False
    
    test_case_location = "{}/class_scheduling_tests/cs_8.pkl".format(LOCATION_PREFIX)

    try:
        with open(test_case_location, 'rb') as f:
            courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

        problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)
        setTO(timeout)

        solutions = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

        if len(solutions) != 3:
            did_fail = True
            details = "Fail Q6 test 13: class scheduling failed to return three solutions"

        for i, s in enumerate(solutions):
            if not check_schedule_solution(problem, s):
                did_fail = True
                details = "Fail Q6 test 13: invalid solution(s) returned by class scheduling"
                break

        setTO(0)

        if not did_fail:
            details = ""
            score = 3

    except TO_exc:
        details = "Got a TIMEOUT while testing class scheduling"
    except (Exception, SystemExit):
        details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

    setTO(0)

    return score, details
    

# @max_grade(3)
# def test_question_6_test_14(modules):
#     stu_propagators = modules[BT_CODE]
#     stu_csp = modules[STUDENT_CSP]
#     stu_const = modules[CONSTRAINTS]

#     score = 0
#     did_fail = False
    
#     test_case_location = "./class_scheduling_tests/cs_7.pkl"

#     with open(test_case_location, 'rb') as f:
#         courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

#     problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)

#     try:
#         setTO(timeout)

#         solns = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

#         if len(solutions) != 8:
#             did_fail = True
#             details = "Fail Q6 test 14: class scheduling failed to return eight solutions"

#         for i, s in enumerate(solns):
#             if not check_schedule_solution(problem, s):
#                 did_fail = True
#                 details = "Fail Q6 test 14: invalid solution(s) returned by class scheduling"
#                 break

#         setTO(0)

#         if not did_fail:
#             details = ""
#             score = 3

#     except TO_exc:
#         details = "Got a TIMEOUT while testing class scheduling"
#     except (Exception, SystemExit):
#         details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

#     setTO(0)

#     return score, details
    

# @max_grade(2)
# def test_question_6_test_15(modules):
#     stu_propagators = modules[BT_CODE]
#     stu_csp = modules[STUDENT_CSP]
#     stu_const = modules[CONSTRAINTS]

#     score = 0
#     did_fail = False
    
#     test_case_location = "./class_scheduling_tests/cs_9.pkl"

#     with open(test_case_location, 'rb') as f:
#         courses, classes, buildings, connected_buildings, slots, rest = pickle.load(f)

#     problem = ScheduleProblem(courses, classes, buildings, connected_buildings, slots, rest)

#     try:
#         setTO(timeout)

#         solns = stu_all.solve_schedules(problem, 'BT', True, 'mrv', True, False)

#         if len(solutions) != 4:
#             did_fail = True
#             details = "Fail Q6 test 15: class scheduling failed to return four solutions"

#         for i, s in enumerate(solns):
#             if not check_schedule_solution(problem, s):
#                 did_fail = True
#                 details = "Fail Q6 test 15: invalid solution(s) returned by class scheduling"
#                 break

#         setTO(0)

#         if not did_fail:
#             details = ""
#             score = 2

#     except TO_exc:
#         details = "Got a TIMEOUT while testing class scheduling"
#     except (Exception, SystemExit):
#         details = "One or more runtime errors occurred while testing class scheduling: %r" % traceback.format_exc()

#     setTO(0)

#     return score, details