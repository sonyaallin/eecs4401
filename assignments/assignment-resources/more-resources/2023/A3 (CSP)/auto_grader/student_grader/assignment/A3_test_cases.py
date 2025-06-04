from assignment.A3_test_cases_aux import *
from utils.test_tools import max_grade

from copy import deepcopy


VARIABLEELIMINATION = "VariableElimination.py"
DECISIONSUPPORT = "DecisionSupport.py"


@max_grade(2)
def restriction_test_1(modules):
    if VARIABLEELIMINATION in modules:
        return t1.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def restriction_test_2(modules):
    if VARIABLEELIMINATION in modules:
        return t2.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def restriction_test_3(modules):
    if VARIABLEELIMINATION in modules:
        return t3.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def restriction_test_4(modules):
    if VARIABLEELIMINATION in modules:
        return t4.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def restriction_test_5(modules):
    if VARIABLEELIMINATION in modules:
        return t5.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"


@max_grade(2)
def summation_test_1(modules):
    if VARIABLEELIMINATION in modules:
        return t6.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def summation_test_2(modules):
    if VARIABLEELIMINATION in modules:
        return t7.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def summation_test_3(modules):
    if VARIABLEELIMINATION in modules:
        return t8.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def summation_test_4(modules):
    if VARIABLEELIMINATION in modules:
        return t9.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(2)
def summation_test_5(modules):
    if VARIABLEELIMINATION in modules:
        return t10.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"


@max_grade(3)
def multiply_test_1(modules):
    if VARIABLEELIMINATION in modules:
        return t11.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(3)
def multiply_test_2(modules):
    if VARIABLEELIMINATION in modules:
        return t12.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(3)
def multiply_test_3(modules):
    if VARIABLEELIMINATION in modules:
        return t13.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(3)
def multiply_test_4(modules):
    if VARIABLEELIMINATION in modules:
        return t14.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(3)
def multiply_test_5(modules):
    if VARIABLEELIMINATION in modules:
        return t15.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"



@max_grade(4)
def VE_test_1(modules):
    if VARIABLEELIMINATION in modules:
        return t16.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_2(modules):
    if VARIABLEELIMINATION in modules:
        return t17.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_3(modules):
    if VARIABLEELIMINATION in modules:
        return t18.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_4(modules):
    if VARIABLEELIMINATION in modules:
        return t19.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_5(modules):
    if VARIABLEELIMINATION in modules:
        return t20.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_6(modules):
    if VARIABLEELIMINATION in modules:
        return t21.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_7(modules):
    if VARIABLEELIMINATION in modules:
        return t22.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_8(modules):
    if VARIABLEELIMINATION in modules:
        return AG_t1.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_9(modules):
    if VARIABLEELIMINATION in modules:
        return AG2_test.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"

@max_grade(4)
def VE_test_10(modules):
    if VARIABLEELIMINATION in modules:
        return AG3_test.test(modules[VARIABLEELIMINATION])
    else:
        return 0, "No VariableElimination.py"




@max_grade(5)
def Q2_test_1(modules):
    if DECISIONSUPPORT in modules:
        return medtest1.test(modules[DECISIONSUPPORT])
    else:
        return 0, "No DecisionSupport.py"

@max_grade(5)
def Q2_test_2(modules):
    if DECISIONSUPPORT in modules:
        return medtest2.test(modules[DECISIONSUPPORT])
    else:
        return 0, "No DecisionSupport.py"

@max_grade(5)
def Q2_test_3(modules):
    if DECISIONSUPPORT in modules:
        return medtest3.test(modules[DECISIONSUPPORT])
    else:
        return 0, "No DecisionSupport.py"

@max_grade(5)
def Q2_test_4(modules):
    if DECISIONSUPPORT in modules:
        return medtest4.test(modules[DECISIONSUPPORT])
    else:
        return 0, "No DecisionSupport.py"

@max_grade(5)
def Q2_test_5(modules):
    if DECISIONSUPPORT in modules:
        return medtest5.test(modules[DECISIONSUPPORT])
    else:
        return 0, "No DecisionSupport.py"

