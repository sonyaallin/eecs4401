from cspbase import *
from tenner_csp_soln import *
from propagators_soln import *

from utilities import TO_exc, setTO
import traceback

timeout = 30

test_ord_mrv = True;
test_model = True;
FC_tests = True;

grid_1 = ([[-1, 0, 1,-1, 9,-1,-1, 5,-1, 2],
       [-1, 7,-1,-1,-1, 6, 1,-1,-1,-1],
       [-1,-1,-1, 8,-1,-1,-1,-1,-1, 9],
       [ 6,-1, 4,-1,-1,-1,-1, 7,-1,-1],
       [-1, 1,-1, 3,-1,-1, 5, 8, 2,-1]],
      [29,16,18,21,24,24,21,28,17,27])

ans_1 = ([3, 0, 1, 7, 9, 4, 8, 5, 6, 2,
       9, 7, 5, 3, 0, 6, 1, 2, 8, 4,
       2, 3, 1, 8, 7, 5, 4, 6, 0, 9,
       6, 5, 4, 0, 2, 9, 3, 7, 1, 8,
       9, 1, 7, 3, 6, 0, 5, 8, 2, 4])

answer_1 = ([[3, 0, 1, 7, 9, 4, 8, 5, 6, 2],
       [9, 7, 5, 3, 0, 6, 1, 2, 8, 4],
       [2, 3, 1, 8, 7, 5, 4, 6, 0, 9],
       [6, 5, 4, 0, 2, 9, 3, 7, 1, 8],
       [9, 1, 7, 3, 6, 0, 5, 8, 2, 4]],
      [29,16,18,21,24,24,21,28,17,27])

grid_2 = ([[-1,-1, 3,-1, 5,-1,-1,-1, 6,-1],
       [ 6,-1, 5, 9, 3, 8,-1,-1,-1,-1],
       [-1, 0,-1,-1,-1,-1, 6,-1, 8, 5],
       [ 2, 5,-1, 9,-1,-1,-1,-1, 3,-1]],
      [18,12,19,27,18,19,15,17,19,16])

ans_2 = ([ 1, 0, 3, 8, 5, 2, 4, 9, 6, 7,
        6, 7, 5, 9, 3, 8, 1, 0, 2, 4,
        9, 0, 3, 1, 4, 2, 6, 7, 8, 5,
        2, 5, 8, 9, 6, 7, 4, 1, 3, 0])

answer_2 = ([[ 1, 0, 3, 8, 5, 2, 4, 9, 6, 7],
       [ 6, 7, 5, 9, 3, 8, 1, 0, 2, 4],
       [ 9, 0, 3, 1, 4, 2, 6, 7, 8, 5],
       [ 2, 5, 8, 9, 6, 7, 4, 1, 3, 0]],
      [18,12,19,27,18,19,15,17,19,16])

grid_3 = ([[ 1, 5, 4, 7,-1,-1,-1,-1, 2,-1],
       [-1,-1,-1, 5, 8, 1, 2, 7, 4,-1],
       [-1,-1, 4, 7, 2, 9,-1,-1,-1, 1],
       [ 3,-1, 1, 8,-1,-1, 2, 6,-1, 4],
       [ 0, 9, 6, 2, 1, 3, 4, 5,-1, 7],
       [ 5,-1, 1,-1,-1, 6, 8, 7, 3, 9]],
      [18,28,22,33,20,27,19,41,26,36])

ans_3 = ([ 1, 5, 4, 7, 9, 3, 0, 8, 2, 6,
        3, 0, 6, 5, 8, 1, 2, 7, 4, 9,
        6, 5, 4, 7, 2, 9, 3, 8, 0, 1,
        3, 7, 1, 8, 0, 5, 2, 6, 9, 4,
        0, 9, 6, 2, 1, 3, 4, 5, 8, 7,
        5, 2, 1, 4, 0, 6, 8, 7, 3, 9])

answer_3 = ([[ 1, 5, 4, 7, 9, 3, 0, 8, 2, 6],
       [ 3, 0, 6, 5, 8, 1, 2, 7, 4, 9],
       [ 6, 5, 4, 7, 2, 9, 3, 8, 0, 1],
       [ 3, 7, 1, 8, 0, 5, 2, 6, 9, 4],
       [ 0, 9, 6, 2, 1, 3, 4, 5, 8, 7],
       [ 5, 2, 1, 4, 0, 6, 8, 7, 3, 9]],
      [18,28,22,33,20,27,19,41,26,36])

if __name__ == "__main__":

    if test_model:

        print("Testing model ....")

        score = 1

        csp, var_array = tenner_csp_model_2(grid_1)
        cons = csp.get_all_cons()

        bin1 = 0
        for c in cons:
            if (len(c.get_scope()) != 2 and len(c.get_scope()) != len(grid_1[0])):
                bin1 +=1

        if bin1 == 0:
            print("Model looks binary")
        else:
            print("Model looks n-ary")


        #1st model test
        print("Testing model ...")

        csp, var_array = tenner_csp_model_1(grid_1)
        cons = csp.get_all_cons()

        bin_flag = True
        for c in cons:
            if (len(c.get_scope()) != 2 and len(c.get_scope()) != len(grid_1[0])):
                bin_flag = False
                break
        if bin_flag: 
            print("Model looks binary")
        else:
            print("Model looks n-ary")

        try:
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_GAC, var_ord=ord_mrv)
            setTO(0)
            sol = []
            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())

            if (sol != ans_1):
                print("Wrong solution")
            if ((sol == ans_1) and bin_flag):          
                print("Passed first GAC test using model 1")
            else:
                print("Failed first GAC test using model 1")
        except TO_exc:
            print("Got a TIMEOUT while testing GAC test using model 1")
        except Exception:
             print("One or more runtime errors occurred while testing GAC with model 1: %r" % traceback.format_exc())


    if FC_tests:
        print("FC Tests")  
        csp, var_array = tenner_csp_model_1(grid_1)
        cons = csp.get_all_cons()

        try:
            bin_flag = True
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_FC, var_ord=ord_mrv)
            setTO(0)
            sol = []

            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())
            
            if (sol != ans_1):
                print("Wrong solution")  
      
            if ((sol == ans_1) and bin_flag):
                print("Passed first FC test using model 1")
            else:
                print("Failed first FC test using model 1")
        except TO_exc:
            print("Got a TIMEOUT while testing FC test using model 1")
        except Exception:
                print("One or more runtime errors occurred while testing FC with model 1: %r" % traceback.format_exc())


        #2nd model test
        csp, var_array = tenner_csp_model_1(grid_2)
        cons = csp.get_all_cons()
        bin_flag = True
        for c in cons:
            if (len(c.get_scope()) != 2 and len(c.get_scope()) != len(grid_2[0])):
                bin_flag = False
                print("Non binary constraint")
                break
        if bin_flag: 
            print("No non binary constraints")                
        
        try:
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_GAC, var_ord = ord_mrv)
            setTO(0)
            sol = []
            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())
            if (sol != ans_2):
                print("Wrong solution")                
            if (sol == ans_2):
                print("Passed first GAC test using model 1")
            else:
                print("Failed first GAC test using model 1")
        except TO_exc:
            print("Got a TIMEOUT while testing GAC test using model 1")
        except Exception:
             print("One or more runtime errors occurred while testing GAC with model 1: %r" % traceback.format_exc())

        try:
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_FC, var_ord = ord_mrv)
            setTO(0)            
            sol = []
            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())
            if (sol != ans_2):
                print("Wrong solution")                 
            if (sol == ans_2):
                print("Passed second FC test using model 1")
            else:
                print("Failed second FC test using model 1")            
        except TO_exc:
            print("Got a TIMEOUT while testing FC test using model 1")
        except Exception:
             print("One or more runtime errors occurred while testing FC with model 1: %r" % traceback.format_exc())


        try:
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_GAC, var_ord = ord_mrv)
            setTO(0)            
            sol = []
            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())
            if (sol != ans_2):
                print("Wrong solution")                 
            if (sol == ans_2):
                print("Passed second GAC test using model 1")
            else:
                print("Failed second GAC test using model 1")            
        except TO_exc:
            print("Got a TIMEOUT while testing GAC test using model 1")
        except Exception:
             print("One or more runtime errors occurred while testing FC with model 1: %r" % traceback.format_exc())



        #3rd model test
        csp, var_array = tenner_csp_model_1(grid_3)
        cons = csp.get_all_cons()
        bin_flag = True
        for c in cons:
            if (len(c.get_scope()) != 2 and len(c.get_scope()) != len(grid_3[0])):
                bin_flag = False
                print("Non binary constraint")
                break
        if bin_flag: 
            print("No non binary constraints")                
        try:
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_GAC, var_ord=ord_mrv)
            setTO(0)  

            sol = []
            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())
            if (sol != ans_3):
                print("Wrong solution")              
            if (sol == ans_3):
                print("Passed third GAC test using model 1")
            else:
                print("Failed third GAC test using model 1")
        except TO_exc:
            print("Got a TIMEOUT while testing GAC test using model 1")
        except Exception:
             print("One or more runtime errors occurred while testing GAC with model 1: %r" % traceback.format_exc())
           
        try:
            setTO(timeout)
            solver = BT(csp)
            solver.bt_search(prop_FC, var_ord=ord_mrv)
            setTO(0)                
            sol = []
            for v in csp.get_all_vars():
                sol.append(v.get_assigned_value())
            if (sol != ans_3):
                print("Wrong solution")                   
            if (sol == ans_3):
                print("Passed third FC test using model 1")
            else:
                print("Failed third FC test using model 1")            
        except TO_exc:
            print("Got a TIMEOUT while testing FC test using model 1")
        except Exception:
             print("One or more runtime errors occurred while testing FC with model 1: %r" % traceback.format_exc())


    if test_ord_mrv:

        print("Ord MRV Tests")

        a = Variable('A', [1])
        b = Variable('B', [1])
        c = Variable('C', [1])
        d = Variable('D', [1])
        e = Variable('E', [1])

        simpleCSP = CSP("Simple", [a,b,c,d,e])

        count = 0
        for i in range(0,len(simpleCSP.vars)):
            simpleCSP.vars[count].add_domain_values(range(0, count))
            count += 1

        var = []
        var = ord_mrv(simpleCSP)

        if var:
            if((var.name) == simpleCSP.vars[0].name):
                print("Passed First Ord MRV Test")
            else:
                print("Failed First Ord MRV Test")
        else:
           print("No Variable Returned from Ord MRV")

        a = Variable('A', [1,2,3,4,5])
        b = Variable('B', [1,2,3,4])
        c = Variable('C', [1,2])
        d = Variable('D', [1,2,3])
        e = Variable('E', [1])

        simpleCSP = CSP("Simple", [a,b,c,d,e])

        var = []
        var = ord_mrv(simpleCSP)

        if var:
            if((var.name) == simpleCSP.vars[len(simpleCSP.vars)-1].name):
                print("Passed Second Ord MRV Test")
            else:
                print("Failed Second Ord MRV Test")
        else:
           print("No Variable Returned from Ord MRV")