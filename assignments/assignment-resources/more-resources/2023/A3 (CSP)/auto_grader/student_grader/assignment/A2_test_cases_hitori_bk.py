import sys
from cspbase import *
from propagators import *
import itertools
import traceback
import statistics

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM
from utils.test_tools import max_grade
from utils.A2_helpers import *
from .test_cases_helpers import *

HITORI = 'hitori_csp.py'
ORDERINGS = 'orderings.py'
DEFAULT_TIMEOUT = 20

##############
##MODEL TEST CASES (HITORI)

##Checking that variables are initialized with correct domains in model 1.
##Passing this test is a prereq for passing check_model_1_constraints.
@max_grade(1)
def model_1_import(stu_models):

    stu_models = stu_models[HITORI]

    score = 0
    try:
        board = [[1, 3, 4, 1], [3, 1, 2, 4],[2, 4, 2, 3], [1, 2, 3, 2]]
        answer = [[0, 1], [0, 3], [0, 4], [0, 1], [0, 3], [0, 1], [0, 2], [0, 4], [0, 2], [0, 4], [0, 2], [0, 3], [0, 1], [0, 2], [0, 3], [0, 2]]

        csp, var_array = stu_models.hitori_csp_model_1(board)
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
    except Exception:
        details = "One or more runtime errors occurred while importing board into model 1: %r" % traceback.format_exc()

    return score,details


##Checking that variables are initialized with correct domains in model 2.
##Passing this test is a prereq for passing check_model_2_constraints.
@max_grade(1)
def model_2_import(stu_models):
    
    stu_models = stu_models[HITORI]

    score = 0
    try:
        board = [[1, 3, 4, 1], [3, 1, 2, 4],[2, 4, 2, 3], [1, 2, 3, 2]]
        answer = [[0, 1], [0, 3], [0, 4], [0, 1], [0, 3], [0, 1], [0, 2], [0, 4], [0, 2], [0, 4], [0, 2], [0, 3], [0, 1], [0, 2], [0, 3], [0, 2]]

        csp, var_array = stu_models.hitori_csp_model_2(board)
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
    except Exception:
        details = "One or more runtime errors occurred while importing board into model 2: %r" % traceback.format_exc()

    return score,details


##Checks that model 1 constraints pass when all numbers different in each row and column, and fail when not all different.
@max_grade(1)
def check_model_1_constraints_enum_rewscols(stu_models):

    stu_models = stu_models[HITORI]

    score = 1
    details = []
    try:
        # do not use inequalities here
        # must be converted to hitori board
        board = [[3, 2, 1],[1, 3, 2],[3, 1, 2]]

        csp, var_array = stu_models.hitori_csp_model_1(board)

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
                    return 0,details

    except Exception:
        details.append("One or more runtime errors occurred while testing constraints in model 1: %r" % traceback.format_exc())
        details = "\n".join(details)
        return 0,details

    details.append("")
    details = "\n".join(details)
    return score,details

##Checks that model 2 constraints pass when all numbers different in each row and column, and fail when not all different.
@max_grade(1)
def check_model_2_constraints_enum_rewscols(stu_models):
    stu_models = stu_models[HITORI]

    score = 1
    details = []
    try:

        board = [[3, 2, 1],[1, 3, 2],[3, 1, 2]]

        csp, var_array = stu_models.hitori_csp_model_2(board)

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
                    return 0,details

    except Exception:
        details.append("One or more runtime errors occurred while testing constraints in model 2: %r" % traceback.format_exc())
        details = "\n".join(details)
        return 0,details

    details.append("")
    details = "\n".join(details)
    return score,details

##Checks that students only have constraints over two variables for model 1.
@max_grade(2)
def check_binary_constraint_model_1(stu_models):

    stu_model = stu_models[HITORI]    
    score = 2

    try:
        #must be converted to hitori board
        board = [[1, 3, 4, 1], [3, 1, 2, 4],[2, 4, 2, 3], [1, 2, 3, 2]]

        csp,var_array = stu_model.hitori_csp_model_1(board)

        all_cons = csp.get_all_cons()

        for con in all_cons:
            all_vars = con.get_scope()

            if len(all_vars) != 2:
                return 0, "Model 1 specifies ONLY binary constraints. Found a constraint of length %d" % len(all_vars)
        return score, ""

    except Exception:
        details = "One or more runtime errors occurred while testing model 1: %r" % traceback.format_exc()
    return 0, details

##Checks that students only have constraints over n variables in model 2.
@max_grade(2)
def check_nary_constraint_model_2(stu_models):

    stu_model = stu_models[HITORI]     
    score = 2

    try:
        #must be converted to hitori board        
        board = [[1, 3, 4, 1], [3, 1, 2, 4],[2, 4, 2, 3], [1, 2, 3, 2]]

        csp,var_array = stu_model.hitori_csp_model_2(board)

        all_cons = csp.get_all_cons()

        saw_nary = False

        for con in all_cons:
            all_vars = con.get_scope()

            if len(all_vars) != 4:
                return 0, "Model 2 specifies ONLY n-ary constraints. Found a constraint of length %d" % len(all_vars)

            return score, ""

    except Exception:
        details = "One or more runtime errors occurred while testing model 2: %r" % traceback.format_exc()
    return 0, details

##Checks that BT fails to assign values to variables given students' constraints when problem is unsolvable in model 1.
@max_grade(4)
def test_UNSAT_problem_model_1(stu_models):

    stu_model = stu_models[HITORI]   
    stu_orderings = stu_models[ORDERINGS]       

    score = 4
    try:
        board = [[3, 3, 3], [3, 3, 3], [3, 3, 3]]

        csp,var_array = stu_model.hitori_csp_model_1(board)

        solver = BT(csp)
        solver.bt_search(prop_BT, stu_orderings.ord_mrv, stu_orderings.val_arbitrary)

        for i in range(len(var_array)):
            for j in range(len(var_array)):
                if var_array[i][j].get_assigned_value() is not None:
                    #return 0,"FAILED\n cell [%d][%d] assigned %r; but problem is unsovable" % (i,j,var_array[i][j].get_assigned_value())
                    return 0,"Failed model 1 test: 'solved' unsolvable problem"

        return score, ""

    except Exception:

        details = "One or more runtime errors occurred while testing model 1 and an unsolvable problem: %r" % traceback.format_exc()
    return 0,details

##Checks that BT fails to assign values to variables given students' constraints when problem is unsolvable in model 1.
@max_grade(4)
def test_UNSAT_problem_model_2(stu_models):

    stu_model = stu_models[HITORI]   
    stu_orderings = stu_models[ORDERINGS]     

    score = 4
    try:
        board = [[3, 3, 3], [3, 3, 3], [3, 3, 3]]

        csp,var_array = stu_model.hitori_csp_model_2(board)

        solver = BT(csp)
        solver.bt_search(prop_BT, stu_orderings.ord_mrv, stu_orderings.val_arbitrary)
        for i in range(len(var_array)):
            for j in range(len(var_array)):
                if var_array[i][j].get_assigned_value() is not None:
                    #return 0,"FAILED\n cell [%d][%d] assigned %r; but problem is unsovable" % (i,j,var_array[i][j].get_assigned_value())
                    return 0,"Failed model 2 test: 'solved' unsolvable problem"

        return score, ""

    except Exception:
        details = "One or more runtime errors occurred while testing model 2 and an unsolvable problem: %r" % traceback.format_exc()
    return 0,details

# ##Checks that small solution of a single grid is initialized correctly.
# ##In binary case there should be no constraints created, in n-ary case there should be 0 or 2 constraints (one for row, col).
@max_grade(1)
def test_small_case(stu_models):
    score = 2
    stu_orderings = stu_models[ORDERINGS] 
    stu_model = stu_models[HITORI]         
    try:
        board = [[1]]
        answer = [0, 1]

        csp, var_array = stu_model.hitori_csp_model_1(board)
        if len(csp.get_all_cons()) != 0 and len(csp.get_all_cons()) != 2:
            return 0, "Failed small test: not the right number of constraints, have %d constraints" % len(csp.get_all_cons())
        if csp.get_all_vars()[0].domain() != answer:
            return 0, "Failed small test: domain of single variable is not correct."

        return 1, ""

    except Exception:
        details = "One or more runtime errors occurred while using %s on a large problem: %r" % (
            name, traceback.format_exc())

    return 0, details

# ##Checks that the satisfying tuples for each constraint are initialized correclty.
@max_grade(1)
def test_sat_tuples(stu_models):
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    stu_model = stu_models[HITORI]     
    try:
        board = [[1, 2], [2, 1]]
        sat_tuples_1 = [[1, 2], [0, 2], [1, 0]]
        sat_tuples_2 = [[2, 1], [2, 0], [0, 1]]

        csp, var_array = stu_model.hitori_csp_model_1(board)
        i = 0
        for con in csp.get_all_cons():
            if len(con.sat_tuples) > 3:
                return 0, "Failed sat_tuples test, too many satisfying tuples."
            if con.get_scope()[0].domain() == [0, 1]:
               for tuple in sat_tuples_1:
                   if not con.check(tuple):
                       print(tuple)
                       return 0, "Failed sat_tuples test, missing a satisfying tuple."
            else:
                for tuple in sat_tuples_2:
                    if not con.check(tuple):
                        print(tuple)
                        return 0, "Failed sat_tuples test, missing a satisfying tuple."

        return score, ""

    except Exception:
        details = "One or more runtime errors occurred while using %s on a large problem: %r" % (
        name, traceback.format_exc())

    return 0, details


# ##Checks that students' code is able to encode proper constraints over some problem.
@max_grade(5)
def test_full_run(stu_models):
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    stu_model = stu_models[HITORI]     

    try:
        board = [[2, 2, 2, 4, 2],
                [5, 1, 4, 2, 3],
                [5, 4, 2, 3, 5],
                [4 ,1, 1, 1, 2],
                [2, 3, 5, 1, 2]]

        setTO(timeout)
        csp,var_array = stu_model.hitori_csp_model_1(board)
        solver = BT(csp)
        solver.bt_search(prop_BT, stu_orderings.ord_mrv, stu_orderings.val_arbitrary)
        setTO(0)

        if check_solution(var_array):
            score = 5
            details = ""
        else:
            details = "Solution found in full run with MRV heuristic on %s was not a valid Hitori solution." % name

    except Exception:

        details = "One or more runtime errors occurred while trying a full run on %s: %r" % (name, traceback.format_exc())

    if score < 5:
        try:
            board = [[2, 2, 2, 4, 2],
                     [5, 1, 4, 2, 3],
                     [5, 4, 2, 3, 5],
                     [4, 1, 1, 1, 2],
                     [2, 3, 5, 1, 2]]


            csp,var_array = stu_model.hitori_csp_model_1(board)
            solver = BT(csp)
            solver.bt_search(prop_BT, stu_orderings.ord_dh, stu_orderings.val_arbitrary)

            if check_solution(var_array):
                score = 5
                details = ""
            else:
                details = "Solution found in full run with DH heuristic on %s was not a valid Hitori solution." % name
        except Exception:
            details = "One or more runtime errors occurred while trying a full run on %s: %r" % (name, traceback.format_exc())

    if score < 5:
        try:
            board = [[2, 2, 2, 4, 2],
                     [5, 1, 4, 2, 3],
                     [5, 4, 2, 3, 5],
                     [4, 1, 1, 1, 2],
                     [2, 3, 5, 1, 2]]

            csp,var_array = stu_model.hitori_csp_model_1(board)
            solver = BT(csp)
            solver.bt_search(prop_BT, stu_orderings.ord_random, stu_orderings.val_lcv)

            if check_solution(var_array):
                score = 5
                details = ""
            else:
                details = "Solution found in full run with LCV heuristic on %s was not a valid Hitori solution." % name
        except Exception:
            details = "One or more runtime errors occurred while trying a full run on %s: %r" % (name, traceback.format_exc())

    return score,details

@max_grade(1)
def test_ord_dh(stu_models):
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    stu_model = stu_models[HITORI] 

    score = 0
    details = ""

    board = [[2, 2, 2, 4, 2],
            [5, 1, 4, 2, 3],
            [5, 4, 2, 3, 5],
            [4, 1, 1, 1, 2],
            [2, 3, 5, 1, 2]]

    assigned = [[0, 0, 0, 0, 0],
                [1, 1, 1, 1, 0],
                [1, 1, 1, 0, 0],
                [1, 1, 0, 0, 0],
                [1, 0, 0, 0, 0]]    

    try:
        csp,var_array = stu_model.hitori_csp_model_1(board)

        count = 0
        for i in range(0,len(board)):
            for j in range(0,len(board[0])):
                if (assigned[i][j]):
                    csp.vars[count].assign(board[i][j])
                count += 1

        var = stu_orderings.ord_dh(csp)

        if((var.name) == csp.vars[4].name):
            return 1, ""

        return 0, "Failed to locate the variable with the highest degree."

    except Exception:
        details = "One or more runtime errors occurred while trying to test ord_dh."

    return 0, details

@max_grade(1)
def test_ord_mrv(stu_models):
    
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    stu_model = stu_models[HITORI] 
    board = [[2, 2, 2, 4, 2], [5, 1, 4, 2, 3], [5, 4, 2, 3, 5], [4 ,1, 1, 1, 2], [2, 3, 5, 1, 2]]   
    
    try: 
 
        csp,var_array = stu_model.hitori_csp_model_2(board)

        count = 0
        for i in range(0,len(board)):
            for j in range(0,len(board[0])):
                csp.vars[count].add_domain_values(range(0, count))
                count += 1

        var = stu_orderings.ord_mrv(csp)

        if((var.name) == csp.vars[0].name):
            return 1, ""

    except Exception:
        details = "One or more runtime errors occurred while trying to test ord_mrv"

    return 0, details

#######JOANNA ADDED THESE!

##Test of CUSTOM ordering on nQueens board
@max_grade(1)
def test_custom_ord_1(stu_models):    
    score = [0, 0]
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    timeout = DEFAULT_TIMEOUT
    decisions = []
    prunings = []
    sumP = 0
    sumD = 0

    try:
        
        for i in range(0,5):
            nQueensCSP = nQueens(10)     
            setTO(timeout)       
            solver = BT(nQueensCSP)
            solver.bt_search(prop_FC, stu_orderings.ord_mrv, stu_orderings.val_arbitrary)   
            setTO(0)
            decisions.append(solver.nDecisions) 
            prunings.append(solver.nPrunings)
            nQueensCSP.print_soln()

        score = [statistics.mean(prunings), statistics.mean(decisions), statistics.stdev(prunings), statistics.stdev(decisions)]
    
        decisions = []
        prunings = []

        for i in range(0,5):
            nQueensCSP = nQueens(10)     
            setTO(timeout)       
            solver = BT(nQueensCSP)
            solver.bt_search(prop_FC, stu_orderings.ord_custom, stu_orderings.val_arbitrary)   
            setTO(0)
            decisions.append(solver.nDecisions) 
            prunings.append(solver.nPrunings)
            nQueensCSP.print_soln()

        score.append(statistics.mean(prunings))
        score.append(statistics.mean(decisions))
        score.append(statistics.stdev(prunings))
        score.append(statistics.stdev(decisions))

        details = ""
    except Exception:
        details.add("Got TIMEOUT while testing test_custom_ord_1")
    except:
        details.add("A runtime error occurred while testing test_custom_ord_1: %r" % traceback.format_exc())

    return score,details    

##Test of CUSTOM ordering on Hitori board
# @max_grade(1)
# def test_custom_ord_2(stu_models):    
#     score = [0, 0, 0]
#     max_score = 1
#     stu_orderings = stu_models[ORDERINGS] 
#     timeout = DEFAULT_TIMEOUT

#     try:

#         #setTO(timeout)

#         board = [[8 ,8, 1, 11, 8, 5, 3, 7, 8, 9, 12, 8],
#                  [1, 8 ,8, 1, 9, 1, 12 ,6, 5, 2, 7 , 4],
#                  [8, 5, 2, 7, 10, 4, 3, 9, 6, 10, 1, 12],
#                  [8, 3, 1, 1, 9, 2, 6, 6, 7, 12, 7, 10],
#                  [7, 3, 11, 8, 4, 5, 10, 5, 4, 3, 6, 4],
#                  [10, 12, 2, 2, 2, 9, 10, 4, 1, 9, 11, 6],
#                  [4, 8, 10, 10, 6, 1, 9, 5, 3, 7, 4, 8],
#                  [11, 1, 7, 10, 9, 12, 1, 2, 5, 4, 3, 9],
#                  [7, 10, 10, 12, 7, 3 , 2, 1, 9, 3, 4, 11],
#                  [12, 9, 4, 12, 3, 5, 7, 5, 11, 1, 1, 5],
#                  [5, 7, 11, 4, 3, 6, 5, 3, 9, 8, 10 ,2],
#                  [10, 2, 5, 3, 1, 10, 4, 8, 12, 7, 9, 9]]

#         #setTO(0)
#         csp, var_array = fn(board)
#         solver = BT(csp)
#         solver.bt_search(prop_FC, stu_orderings.ord_custom, stu_orderings.val_arbitrary)

#         if check_solution(var_array):
#             score = [0, solver.nDecisions, solver.nPrunings]
#         else:
#             score = [1, solver.nDecisions, solver.nPrunings]
        
#         details = ""
#     except Exception:
#         details.add("Got TIMEOUT while testing test_custom_ord_2")
#     except:
#         details.add("A runtime error occurred while testing test_custom_ord_2: %r" % traceback.format_exc())

#     return score,details    

##################
##SIMPLE MRV TESTS

##test MRV with just 3 different sized domains
##and x + y = z
@max_grade(1)
def simple_mrv_1(stu_models):
    
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try: 
        x = Variable('X',[1,2])
        y = Variable('Y',[1,2,3])
        z = Variable('Z',[2])
        sat_tup = sum1([1,2],[1,2,3],[2])
        c1 = Constraint('C1',[x,y,z])
        c1.add_satisfying_tuples(sat_tup)
        simpleCSP = CSP("SimpleEqs1",[x,y,z])
        simpleCSP.add_constraint(c1)
        if stu_orderings.ord_mrv(simpleCSP) == z:
            score = max_score
            details = ""
        else:
            details = "MRV1: supposed to return %s; returned %s" % (str(z), str(stu_orderings.ord_mrv(simpleCSP)))
    except Exception:
        details = "One or more runtime errors occurred in MRV1: %r" % traceback.format_exc()
    return score,details

##test MRV with 3 different size domains, where the largest domain would result in a DWO
@max_grade(1)
def simple_mrv_2(stu_models):
    
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try: 
        x = Variable('X',[1,2])
        y = Variable('Y',[1,2,3])
        z = Variable('Z',[0,6,7,8,9,10])
        sat_tup = sum1([1,2],[1,2,3],[2])
        c1 = Constraint('C1',[x,y,z])
        c1.add_satisfying_tuples(sat_tup)
        simpleCSP = CSP("SimpleEqs1",[x,y,z])
        simpleCSP.add_constraint(c1)
        if stu_orderings.ord_mrv(simpleCSP) == x:
            score = max_score
            details = ""
        else:
            details = "MRV2: supposed to return %s; returned %s" % (str(x), str(stu_orderings.ord_mrv(simpleCSP)))
    except Exception:
        details = "One or more runtime errors occurred in MRV2: %r" % traceback.format_exc()
    return score,details

##Test MRV after assigning some variables
@max_grade(1)
def simple_mrv_3(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try: 
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])
        w = Variable('W', [1, 2, 3, 4])
        c1 = Constraint('C1', [x,y,z])
        c1.add_satisfying_tuples(sum1([1,2,3],[1,2,3],[1,2,3]))
        c2 = Constraint('C2', [w,z])
        c2.add_satisfying_tuples(less1([1,2,3],[1,2,3,4]))
        simpleCSP = CSP("SimpleEqs",[x,y,z,w])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        x.assign(1)
        z.assign(2)
        if stu_orderings.ord_mrv(simpleCSP) == y:
            score = max_score
            details = ""
        else:
            details = "MRV3: supposed to return %s; returned %s" % (str(y), str(stu_orderings.ord_mrv(simpleCSP)))
    except Exception:
        details = "One or more runtime errors occurred in MRV3: %r" % traceback.format_exc()
    return score,details

###### DO SOME CHECKS WITH FC FOR MRV for nqueens
##TODO 
@max_grade(1)
def n_queens_mrv_4(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        csp = nQueens(8)
        v = csp.vars[0]	
        v.assign(1)
        prop_FC(csp,v)
        v2 = csp.vars[1]
        v2.assign(3)
        prop_FC(csp,v2)
        v3 = csp.vars[3]
        v3.assign(8)
        prop_FC(csp,v3)
        v4 = csp.vars[4]
        v4.assign(4)
        prop_FC(csp,v4)
        if stu_orderings.ord_mrv(csp) == csp.vars[6]:
            score = max_score
            details = ""
        else:
            details = "MRV4: supposed to return %s; returned %s" % (str(csp.vars[6]),str(stu_orderings.ord_mrv(csp)))
    except Exception:
        details = "One or more runtime errors occurred in MRV4: %r" % traceback.format_exc()
    return score,details

######## ORD_DH

##Test DH, two constraints, exactly one variable is shared between two constraints  
@max_grade(1)
def simple_dh_1(stu_models):
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])
        w = Variable('W', [1, 2, 3, 4])
        c1 = Constraint('C1', [x,y,z])
        c1.add_satisfying_tuples(sum1([1,2,3],[1,2,3],[1,2,3]))
        c2 = Constraint('C2', [w,z])
        c2.add_satisfying_tuples(less1([1,2,3],[1,2,3,4]))
        simpleCSP = CSP("SimpleEqs",[x,y,z,w])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        if stu_orderings.ord_dh(simpleCSP) == z:
            score = max_score
            details = ""
        else:
            details = "DH1: supposed to return %s; returned %s" % (str(z), str(stu_orderings.ord_dh(simpleCSP)))
    except Exception:
        details = "One or more runtime errors occurred in DH1: %r" % traceback.format_exc()
    return score,details

##Test DH, where two variables are in a ton of repeated constraints but only have a constraint graph of 3 each, but another that is in fewer constraints has a constraint graph of 4. 
@max_grade(1)
def simple_dh_2(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        xdom = [1,2,3]
        ydom = [1,2,3]
        zdom = [1,2,3]
        wdom = [1,2,3,4]
        x = Variable('x', xdom)
        y = Variable('y', ydom)
        z = Variable('z', zdom)
        w = Variable('w', wdom)
        c1 = Constraint('c1', [x,z])
        c1.add_satisfying_tuples(less2(xdom,zdom))
        c2 = Constraint('c2', [y,z])
        c2.add_satisfying_tuples(less2(ydom,zdom))
        c3 = Constraint('c3', [w,z])
        c3.add_satisfying_tuples(less2(wdom,zdom))
        c4 = Constraint('c4', [x,y])
        c4.add_satisfying_tuples(minus_even(xdom,ydom))
        c5 = Constraint('C5', [x,y])
        c5.add_satisfying_tuples(sum_less5(xdom,ydom))
        c6 = Constraint('C6', [x,y])
        c6.add_satisfying_tuples(plus_double_4(xdom,ydom))
        c7 = Constraint('C7', [x,y])
        c7.add_satisfying_tuples(minus_pos(xdom,ydom))
        simpleCSP = CSP("SimpleEqs",[x,y,z,w])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        simpleCSP.add_constraint(c3)
        simpleCSP.add_constraint(c4)
        simpleCSP.add_constraint(c5)
        simpleCSP.add_constraint(c6)
        simpleCSP.add_constraint(c7)

        if stu_orderings.ord_dh(simpleCSP) == z:
            score = max_score
            details = ""
        else:
            details = "DH2: supposed to return %s; returned %s" % (str(z), str(stu_orderings.ord_dh(simpleCSP)))
    except Exception:
        details = "One or more runtime errors occurred in DH2: %r" % traceback.format_exc()
    return score,details


##ADD SOME DH + FC

##ADD SOME n-queens + FC + DH
####################################
##Simple LCV tests

##Since we didn't give them anything to go off of, this one just checks that it runs without any runtime errors.
@max_grade(1)
def simplest_lcv_1(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])
        w = Variable('W', [1, 2, 3, 4])

        c1 = Constraint('C1', [x,y,z])
        c1.add_satisfying_tuples(sum1([1,2,3],[1,2,3],[1,2,3]))
        c2 = Constraint('C2', [w,z])
        c2.add_satisfying_tuples(less1([1,2,3],[1,2,3,4]))
        simpleCSP = CSP("SimpleEqs",[x,y,z,w])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        stu_orderings.val_lcv(simpleCSP,w)
        score = max_score
        details = ""
    except Exception:
        details = "One or more runtime errors occurred in LCV1: %r" % traceback.format_exc()
    return score,details

@max_grade(1)
def lcv_base_case_2(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        x_dom = [1,2,3]
        y_dom = [1,2,3]
        z_dom = [3,4,5]
        x = Variable('X', x_dom)
        y = Variable('Y', y_dom)
        z = Variable('Z', z_dom)
        c1 = Constraint('C1', [x,y,z])
        c1.add_satisfying_tuples(sum_big1(x_dom,y_dom,z_dom))
        simpleCSP = CSP("SimpleEqs",[x,y,z])
        simpleCSP.add_constraint(c1)
        if stu_orderings.val_lcv(simpleCSP,x) == [3,2,1]:
            score = max_score
            details = ""
        else:
            details = "LCV2: supposed to return [3,2,1]; returned %s" % str(stu_orderings.val_lcv(simpleCSP))
    except Exception:
        details = "One or more runtime errors occurred in LCV2: %r" % traceback.format_exc()
    return score,details

##Can't use just the original domains
##edge case
##partial score for getting it correct before assignment
@max_grade(1)
def lcv_test_curr_domain5(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        csp = nQueens(8)
        v = csp.vars[0]
        v2 = csp.vars[7]
        first = stu_orderings.val_lcv(csp,v2)
        ans1 = set(first)
        corr1 = set([1,2,3,4,5,6,7,8])
        v.assign(1)
        prop_FC(csp,v)
        ans2 = stu_orderings.val_lcv(csp,v2)
        ans2 = set(ans2)
        corr2 = set([7,6,2,3,4,5,6])
        if corr1 == ans1 and corr2 == ans2:
            score = max_score 
            details = ""
        elif corr1 == ans1:
            score = partial
            details = "Answer did not properly update to include change in current domain for LCV5. Domain should include: %r; returned %r" % (corr2,ans2)
        else:
            details = "LCV5: Domain not correct. Should be: %r; returned: %r" % (corr1,ans1)

    except Exception:
        details = "One or more runtime errors occured in LCV5: %r" % traceback.format_exc()

    return score,details
			
##Just tests a standard case.
@max_grade(1)
def lcv_test_curr_domain3(stu_models):
    
    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        x_dom = [1,2,3]
        y_dom = [1,2,3] 
        z_dom = [3,4,5]
        x = Variable('x',x_dom)
        y = Variable('y',y_dom)
        z = Variable('z',z_dom)
        c1 = Constraint('C1', [x,y,z])
        c1.add_satisfying_tuples(sum_less1(x_dom,y_dom,z_dom))
        c2 = Constraint('C2',[x,y])
        c2.add_satisfying_tuples(minus_even(x_dom,y_dom))
        simpleCSP = CSP("SimpleEqs",[x,y,z])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        if stu_orderings.val_lcv(simpleCSP,x) == [1,2,3] or stu_orderings.val_lcv(simpleCSP,x) == [1,3,2]:
            details = ""
        else:
            details = "LCV3, before assign was supposed to return 1 first; returned %r first" % stu_orderings.val_lcv(simpleCSP,x)[0]
    
    except Exception:
        details = "One or more runtime errors occured in LCV3: %r" % traceback.format_exc()
    return score,details

##Tests that we actually returned a list
@max_grade(1)
def simplest_lcv_4(stu_models):

    score = 0
    max_score = 1
    stu_orderings = stu_models[ORDERINGS] 
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])
        w = Variable('W', [1, 2, 3, 4])
        c1 = Constraint('C1', [x,y,z])
        c1.add_satisfying_tuples(sum1([1,2,3],[1,2,3],[1,2,3]))
        c2 = Constraint('C2', [w,z])
        c2.add_satisfying_tuples(less1([1,2,3],[1,2,3,4]))
        simpleCSP = CSP("SimpleEqs",[x,y,z,w])
        simpleCSP.add_constraint(c1)
        simpleCSP.add_constraint(c2)
        output = stu_orderings.val_lcv(simpleCSP,w)
        if type(output) is list:
            score = max_score
            details = ""
        else:
            details = "LCV was supposed to return a list. Instead returned %r" % type(output)

    except Exception:
        details = "One or more runtime errors occurred in LCV1: %r" % traceback.format_exc()
    return score,details



