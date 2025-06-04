#!/usr/bin/env python
import os  # for time functions
import traceback

from utils.utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM

from utils.test_tools import max_grade
from .test_cases_helpers import *
from dependencies.A4_test_cases import *

SOLUTION = 'solution.py'
DEFAULT_TIMEOUT = 2


#VE TESTS (worth 25) 14+11 = 25
@max_grade(2)
def ve_test_1(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    Asia = Parameters[0]
    Smoking = Parameters[2]
    Bronchitis = Parameters[5]

    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("VE Test 1 ....")
        Smoking.set_evidence('smoker')
        probs = stu_solution.VE(Asia, Bronchitis, [Smoking])
        if abs(probs[0] - 0.6) < 0.002 and abs(probs[1] - 0.4) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Bronchitis=present|Smoking=smoker) = {} P(Bronchitis=absent|Smoking=smoker) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_1: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(2)
def ve_test_2(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Dyspnea = Parameters[7]
    Tuberculosis = Parameters[3]
    
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("VE Test 2 ....")
        Tuberculosis.set_evidence('present')
        probs = stu_solution.VE(Asia, Dyspnea, [Tuberculosis])
        if abs(probs[0] - 0.789) < 0.002 and abs(probs[1] - 0.21) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Xray=normal|TBorCA=true) = {} P(Xray=abnormal|TBorCA=true) = {}'.format(probs[0], probs[1]))
        details.add('P(Xray=normal|TBorCA=true) = 0.789 P(Xray=abnormal|TBorCA=true) = 0.21')

    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_2: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(2)
def ve_test_3(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Dyspnea = Parameters[7]
    TBorCA = Parameters[6]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("VE Test 3 ....")
        TBorCA.set_evidence('true')
        probs = stu_solution.VE(Asia, Dyspnea, [TBorCA])
        if abs(probs[0] - 0.8106077620781144) < 0.002 and abs(probs[1] - 0.1893922379218856) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Dyspnea=present|TBorCA=true) = {} P(Dyspnea=absent|TBorCA=true) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_3: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(2)
def ve_test_4(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Smoking = Parameters[2]
    VisitAsia = Parameters[1]
    TBorCA = Parameters[6]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("VE Test 4 ....")
        Smoking.set_evidence('smoker')
        VisitAsia.set_evidence('visit')
        probs = stu_solution.VE(Asia, TBorCA, [VisitAsia, Smoking])
        if abs(probs[0] - 0.145) < 0.002 and abs(probs[1] - 0.855) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(TBorC=true|Smoking=smoker,VisitAsia=visit) = {} P(TBorC=false|Smoking=smoker,VisitAsia=visit) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())
      
    details.add("ve_test_4: ".format(score))
    details = "\n".join(details)    
    return 2*score, details 

@max_grade(2)
def ve_test_5(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    TBorCA = Parameters[6]
    Xray = Parameters[8]
    VisitAsia = Parameters[1]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("VE Test 5 ....")
        Xray.set_evidence('abnormal')
        VisitAsia.set_evidence('visit')
        probs = stu_solution.VE(Asia, TBorCA, [Xray])
        if abs(probs[0] - 0.5760396859045477) < 0.002 and abs(probs[1] - 0.4239603140954523) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(TBorC=true|Xray=abnormal,VisitAsia=visit) = {} P(TBorC=false|Xray=abnormal,VisitAsia=visit) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_5: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(2)
def ve_test_6(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Cancer = Parameters[4]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("VE Test 6 ....")
        probs = stu_solution.VE(Asia, Cancer, [])
        if abs(probs[0] - 0.055) < 0.002 and abs(probs[1] - 0.945) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Cancer=present) = {} P(Cancer=absent) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())


    details.add("ve_test_6: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(2)
def ve_test_7(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Smoking = Parameters[2]
    Dyspnea = Parameters[7]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)

        details.add("VE Test 7 ....")
        Dyspnea.set_evidence('present')
        probs1 = stu_solution.VE(Asia, Smoking, [Dyspnea])
        Dyspnea.set_evidence('absent')
        probs2 = stu_solution.VE(Asia, Smoking, [Dyspnea])
        if abs(probs1[0] - 0.6339) < 0.0001 and abs(probs1[1] - 0.366) < 0.0001 and abs(probs2[0] - 0.3964) < 0.0001 and abs(probs2[1] - 0.60357) < 0.0001:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(Smoking=smoker|Dyspnea=present) = {} P(Smoking=non-smoker|Dyspnea=present) = {} P(Smoking=smoker|Dyspnea=absent) = {} P(Smoking=non-smoker|Dyspnea=absent) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_7: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(11)
def ve_test_8(student_modules):

    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeQ3()
    #[Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
    Q3 = Parameters[0]
    E = Parameters[1]
    B = Parameters[2]
    S = Parameters[3]
    G = Parameters[4]
    W = Parameters[5]
    FE = Parameters[6]
    FB = Parameters[7]
    FS = Parameters[8]
    FG = Parameters[9]
    FW = Parameters[10]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)  
        details.add("OVE Test 1 ....")
        G.set_evidence('g')
        probs = stu_solution.VE(Q3, S, [G])
        if probs[0] == 1 and probs[1] == 0:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        
        details.add('P(s|g) = {} P(-s|g) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    #(b)
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OVE Test 2 ....")
        B.set_evidence('b')
        E.set_evidence('-e')
        probs = stu_solution.VE(Q3, W, [B, E])
        if abs(probs[0] - 0.68) < 0.0001 and abs(probs[1] - 0.32) < 0.0001:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")    
    
        details.add('P(w|b,-e) = {} P(-w|b,-e) = {}'.format(probs[0],probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    #(c)
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OVE Test 3 ....")
        S.set_evidence('s')
        probs1 = stu_solution.VE(Q3, G, [S])
        S.set_evidence('-s')
        probs2 = stu_solution.VE(Q3, G, [S])
        if probs1[0] == 0.5 and probs1[1] == 0.5 and probs2[0] == 0.0 and probs2[1] == 1.0:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")  
        details.add('P(g|s) = {} P(-g|s) = {} P(g|-s) = {} P(-g|-s) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    #(d)
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)    
        details.add("OVE Test 4 ....")
        S.set_evidence('s')
        W.set_evidence('w')
        probs1 = stu_solution.VE(Q3, G, [S,W])
        S.set_evidence('s')
        W.set_evidence('-w')
        probs2 = stu_solution.VE(Q3, G, [S,W])
        if probs1[0] == 0.5 and probs1[1] == 0.5 and probs2[0] == 0.5 and probs2[1] == 0.5:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")  
        details.add('P(g|s,w) = {} P(-g|s,w) = {} P(g|s,-w) = {} P(-g|s,-w) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())
   
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OVE Test 5 ....")
        S.set_evidence('-s')
        W.set_evidence('w')
        probs3 = stu_solution.VE(Q3, G, [S,W])
        S.set_evidence('-s')
        W.set_evidence('-w')
        probs4 = stu_solution.VE(Q3, G, [S,W])
        if probs3[0] == 0.0 and probs3[1] == 1.0 and probs4[0] == 0.0 and probs4[1] == 1.0:
          score += 2
          details.add("passed.")
        else:
          details.add("failed.") 
        details.add('P(g|-s,w) = {} P(-g|-s,w) = {} P(g|-s,-w) = {} P(-g|-s,-w) = {}'.format(probs3[0],probs3[1],probs4[0],probs4[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    #(f) 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)    
        details.add("OVE Test 6 ....")
        W.set_evidence('w')
        probs1 = stu_solution.VE(Q3, G, [W])
        W.set_evidence('-w')
        probs2 = stu_solution.VE(Q3, G, [W])
        if abs(probs1[0] - 0.15265998457979954) < 0.0001 and abs(probs1[1] - 0.8473400154202004) < 0.0001 and abs(probs2[0] - 0.01336753983256819) < 0.0001 and abs(probs2[1] - 0.9866324601674318) < 0.0001:
          score += 2
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(g|w) = {} P(-g|w) = {} P(g|-w) = {} P(-g|-w) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    #(h)
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)    
        details.add("OVE Test 7 ....")
        probs = stu_solution.VE(Q3, G, [])
        if abs(probs[0] - 0.04950000000000001) < .0001 and abs(probs[1] - 0.9505) < .0001:
          score += 2
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(g) = {} P(-g) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())
      
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("Test 8 ....")    
        probs = stu_solution.VE(Q3, E, [])
        if abs(probs[0] - 0.1) < 0.0001 and abs(probs[1] - 0.9) < 0.0001:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(e) = {} P(-e) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_tests_8: ".format(score))
    details = "\n".join(details)    
    return score, details


#NORMALIZATION TESTS (WORTH 7)
@max_grade(3)
def norm_test_1(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    details.add("Normalization test 1 ....")
    normalized_nums = stu_solution.normalize([i for i in range(5)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
      details.add("passed.")
      score += 3
    else:
      details.add("failed.")
    details.add('{} when normalized to {} sum to {}'.format([i for i in range(5)], normalized_nums, norm_sum))

    return score, details

@max_grade(2)
def norm_test_2(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    details.add("Normalization test 2 ....")
    normalized_nums = stu_solution.normalize([i for i in range(0,-5,-1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
      details.add("passed.")
      score += 2
    else:
      details.add("failed.")
    details.add('Input when normalized to {} sum to {}'.format(normalized_nums, norm_sum))

    return score, details

@max_grade(2)
def norm_test_3(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    details.add("Normalization test 4 ....")
    normalized_nums = stu_solution.normalize([i for i in range(0,-5,-1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
      details.add("passed.")
      score += 2
    else:
      details.add("failed.")
    details.add('Input when normalized to {} sum to {}'.format(normalized_nums, norm_sum))
    return score, details



#MULTIPLY FACTORS TESTS  (WORTH 7)
@max_grade(1)
def multiply_factors_test_1(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    F2 = Parameters[10]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("MF Test 1 ....")    
        factor = stu_solution.multiply_factors([F2])
        values = (factor.get_value(['smoker']), factor.get_value(['non-smoker']))
        if values[0] == 0.5 and values[1] == 0.5:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(smoker) = {} P(non-smoker) = {}'.format(values[0], values[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())


    details.add("multiply_factors_test_1: ".format(score))
    details = "\n".join(details)    
    return score, details

@max_grade(1)
def multiply_factors_test_2(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    F1 = Parameters[9]
    F2 = Parameters[10]
    VisitAsia = Parameters[1]
    Smoking = Parameters[2]    
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("MF Test 2 ....")    
        factor = stu_solution.multiply_factors([F1, F2])
        tests = []
        values = []
        for val1 in VisitAsia.domain():
          for val2 in Smoking.domain():
            try:
              value = factor.get_value([val1, val2])
              values.append(value)
            except ValueError:
              value = factor.get_value([val2, val1])
              values.append(value)
        if abs(values[0]-0.005) < 0.002 and abs(values[1]-0.005) < 0.002 and abs(values[2]-0.495) < 0.002 and abs(values[3]-0.495) < 0.002:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
   
        details.add('P(visit,smoker) = {} P(no-visit,smoker) = {} P(visit,non-smoker) = {} P(no-visit,non-smoker) = {}'.format(values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())


    details.add("multiply_factors_test_2: ".format(score))
    details = "\n".join(details)    
    return score, details

@max_grade(2)
def multiply_factors_test_3(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    VisitAsia = Parameters[1]
    Bronchitis = Parameters[5] 
    Smoking = Parameters[2]
    F1 = Parameters[9]
    F5 = Parameters[13]        
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("MF Test 3 ....")    
        factor = stu_solution.multiply_factors([F1, F5])
        tests = []
        values = []
        for val1 in VisitAsia.domain():
          for val2 in Bronchitis.domain():
            for val3 in Smoking.domain():
              try:
                value = factor.get_value([val1, val2, val3])
                values.append(value)
              except ValueError:
                try:
                  value = factor.get_value([val3, val2, val1])
                  values.append(value)
                except ValueError:
                  try:
                    value = factor.get_value([val2, val3, val1])
                    values.append(value)
                  except ValueError:
                    try:
                      value = factor.get_value([val3, val1, val2])
                      values.append(value)
                    except ValueError:
                      try:
                        value = factor.get_value([val2, val1, val3])
                        values.append(value)
                      except ValueError:
                        value = factor.get_value([val1, val3, val2])
                        values.append(value)
        expected_values = [0.006, 0.003, 0.004, 0.006999999999999999, 0.594, 0.297, 0.396, 0.693]
        if all([abs(value - ev) < 0.002 for value, ev in zip(values, expected_values)]):
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('F1 x F5 = {}'.format(values))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("multiply_factors_test_3: ".format(score))
    details = "\n".join(details)    
    return 2*score, details


@max_grade(3)
def multiply_factors_test_4(student_modules):

    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeQ3()
    #[Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
    Q3 = Parameters[0]
    E = Parameters[1]
    B = Parameters[2]
    S = Parameters[3]
    G = Parameters[4]
    W = Parameters[5]
    FE = Parameters[6]
    FB = Parameters[7]
    FS = Parameters[8]
    FG = Parameters[9]
    FW = Parameters[10]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OMF Test 1 ....")    
        factor = stu_solution.multiply_factors([FE])
        values = (factor.get_value(['e']), factor.get_value(['-e']))
        if values[0] == 0.1 and values[1] == 0.9:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(e) = {} P(-e) = {}'.format(values[0], values[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OMF Test 2 ....")    
        factor = stu_solution.multiply_factors([FB, FE])
        tests = []
        values = []
        for e_val in E.domain():
          for b_val in B.domain():
            try:
              value = factor.get_value([e_val, b_val])
              values.append(value)
            except ValueError:
              value = factor.get_value([b_val, e_val])
              values.append(value)
            tests.append(value == FE.get_value([e_val])*FB.get_value([b_val]))
        if all(tests):
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(e,b) = {} P(-e,b) = {} P(e,-b) = {} P(-e,-b) = {}'.format(values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OMF Test 3 ....")    
        factor = stu_solution.multiply_factors([FE, FS])
        tests = []
        values = []
        for e_val in E.domain():
          for b_val in B.domain():
            for s_val in S.domain():
              try:
                value = factor.get_value([e_val, b_val, s_val])
                values.append(value)
              except ValueError:
                try:
                  value = factor.get_value([s_val, b_val, e_val])
                  values.append(value)
                except ValueError:
                  try:
                    value = factor.get_value([b_val, s_val, e_val])
                    values.append(value)
                  except ValueError:
                    try:
                      value = factor.get_value([s_val, e_val, b_val])
                      values.append(value)
                    except ValueError:
                      try:
                        value = factor.get_value([b_val, e_val, s_val])
                        values.append(value)
                      except ValueError:
                        value = factor.get_value([e_val, s_val, b_val])
                        values.append(value)
            tests.append(value == FE.get_value([e_val])*FS.get_value([s_val, e_val, b_val]))
        if all(tests):
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")      
        details.add('P(e,s,b) = {} P(-e,s,b) = {} P(e,-s,-b) = {} P(-e,s,-b) = {}'.format(values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())
  
    details.add("multiply_factors_test_4: ".format(score))
    details = "\n".join(details)    
    return score, details

#RESTRICT FACTORS TESTS  (WORTH 7)
@max_grade(1)
def restrict_factor_test_1(student_modules):

    score = 0
    stu_solution = student_modules[SOLUTION]     
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    VisitAsia = Parameters[1]
    F1 = Parameters[9] 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("\nRestrict Factor Tests")
        details.add("RF Test 1 ....")    
        factor = stu_solution.restrict_factor(F1, VisitAsia, 'visit')
        value = factor.get_value_at_current_assignments()
        if value == 0.01:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(VisitAsia=visit) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("restrict_factor_test_1: ".format(score))
    details = "\n".join(details)    
    return score, details

@max_grade(1)
def restrict_factor_test_2(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    Smoking = Parameters[2]
    Bronchitis = Parameters[5]    
    F5 = Parameters[13] 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("RF Test 2 ....")    
        factor = stu_solution.restrict_factor(F5, Smoking, 'non-smoker')
        factor = stu_solution.restrict_factor(factor, Bronchitis, 'absent')
        value = factor.get_value_at_current_assignments()
        if value == 0.7:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Bronchitis=absent|Smoking=non-smoker) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("restrict_factor_test_2: ".format(score))
    details = "\n".join(details)    
    return score, details

@max_grade(2)
def restrict_factor_test_3(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6 14, F7 15, F8]
    TBorCA = Parameters[6]
    Bronchitis = Parameters[5]  
    Dyspnea = Parameters[7]    
    F7 = Parameters[15] 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("RF Test 3 ....")    
        factor = stu_solution.restrict_factor(F7, Dyspnea, 'absent')
        factor = stu_solution.restrict_factor(factor, TBorCA, 'true')
        factor = stu_solution.restrict_factor(factor, Bronchitis, 'present')
        value = factor.get_value_at_current_assignments()
        if value == .1:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Dyspnea=absent|TBorCA=true,Bronchitis=present) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("restrict_factor_test_3: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(3)
def restrict_factor_test_4(student_modules):

    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()
    
    Parameters = makeQ3()
    #[Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
    Q3 = Parameters[0]
    E = Parameters[1]
    B = Parameters[2]
    S = Parameters[3]
    G = Parameters[4]
    W = Parameters[5]
    FE = Parameters[6]
    FB = Parameters[7]
    FS = Parameters[8]
    FG = Parameters[9]
    FW = Parameters[10]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("ORF Test 1 ....")    
        factor = stu_solution.restrict_factor(FE, E, 'e')
        value = factor.get_value_at_current_assignments()
        if value == 0.1:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(E=e) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("ORF Test 2 ....")    
        factor = stu_solution.restrict_factor(FG, S, '-s')
        factor = stu_solution.restrict_factor(factor, G, '-g')
        value = factor.get_value_at_current_assignments()
        if value == 1:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(G=-g|S=s) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("ORF Test 3 ....")    
        factor = stu_solution.restrict_factor(FS, S, '-s')
        factor = stu_solution.restrict_factor(factor, E, '-e')
        factor = stu_solution.restrict_factor(factor, B, 'b')
        value = factor.get_value_at_current_assignments()
        if value == .2:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(S=-s|E=-e,B=b) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())
  
    details.add("restrict_factor_test_4: ".format(score))
    details = "\n".join(details)    
    return score, details    

@max_grade(2)
def sum_out_variable_test_1(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    VisitAsia = Parameters[1]  
    F1 = Parameters[9] 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("SOV Test 1 ....")    
        factor = stu_solution.sum_out_variable(F1, VisitAsia)
        value = factor.get_value_at_current_assignments()
        if value == 1:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('sum P(VisitAsia) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())
       

    details.add("sum_out_variable_test_1: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

#SUM FACTORS TESTS  (WORTH 7)
@max_grade(2)
def sum_out_variable_test_2(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    Smoking = Parameters[2]  
    F4 = Parameters[12] 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("SOV Test 2 ....")    
        factor = stu_solution.sum_out_variable(F4, Smoking)
        values = (factor.get_value(["present"]), factor.get_value(["absent"]))
        tests = (abs(values[0] - 0.11) < 0.002, abs(values[1] - 1.89) < 0.002)
        if all(tests):
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(Cancer = present) = {} P(Cancer = absent) = {} '.format(values[0], values[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())


    details.add("sum_out_variable_test_2: ".format(score))
    details = "\n".join(details)    
    return 2*score, details

@max_grade(1)
def sum_out_variable_test_3(student_modules):
    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()


    Parameters = makeBN()
    #[Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6 14, F7, F8]
    Tuberculosis = Parameters[3]  
    Cancer = Parameters[4]  
    F6 = Parameters[14] 
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("SOV Test 3 ....")    
        factor1 = stu_solution.sum_out_variable(F6, Tuberculosis)
        factor2 = stu_solution.sum_out_variable(factor1, Cancer)
        values = (factor2.get_value(["true"]), factor2.get_value(["false"]))
        tests = (abs(values[0] - 3.0) < 0.002, abs(values[1] - 1.0) < 0.002)
        if all(tests):
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(TBorC = true) = {} P(TBorC = false) = {} '.format(values[0], values[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())


    details.add("sum_out_variable_test_3: ".format(score))
    details = "\n".join(details)    
    return score, details


@max_grade(2)
def sum_out_variable_test_4(student_modules):

    score = 0
    stu_solution = student_modules[SOLUTION] 
    details = set()

    Parameters = makeQ3()
    #[Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
    Q3 = Parameters[0]
    E = Parameters[1]
    B = Parameters[2]
    S = Parameters[3]
    G = Parameters[4]
    W = Parameters[5]
    FE = Parameters[6]
    FB = Parameters[7]
    FS = Parameters[8]
    FG = Parameters[9]
    FW = Parameters[10]
    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)
        details.add("OSOV Test 1 ....")    
        factor = stu_solution.sum_out_variable(FE, E)
        value = factor.get_value_at_current_assignments()
        if value == 1:
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('sum_e P(e) = {}'.format(value))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    try:
        timeout = DEFAULT_TIMEOUT  
        setTO(timeout)     
        details.add("OSOV Test 2 ....")    
        factor = stu_solution.sum_out_variable(FS, E)
        values = (factor.get_value(["s", "b"]), factor.get_value(["s", "-b"]), factor.get_value(["-s", "b"]), factor.get_value(["-s", "-b"]))
        tests = (abs(values[0] - 1.7) < 0.002, abs(values[1] - 0.2) < 0.002, abs(values[2] - 0.3) < 0.002, abs(values[3] - 1.8) < 0.002)
        if all(tests):
          score += 1
          details.add("passed.")
        else:
          details.add("failed.")
        details.add('P(S = s | B = b) = {} P(S = s | B = -b) = {} P(S = -s | B = b) = {} P(S = -s | B = -b) = {}'.format(values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("sum_out_variable_test_4: ".format(score))
    details = "\n".join(details)    
    return score, details




