#!/usr/bin/env python
import os  # for time functions
import traceback
import sys
import re
import importlib
import subprocess
import itertools
import csv

from utilities import sortInnerMostLists, TO_exc, setTO, setMEM, resetMEM
from bnetbase import Variable, Factor, BN, adultDatasetBN, adultDatasetBN2

SOLUTION = 'solution.py'
DEFAULT_TIMEOUT = 2


def makeBN():

     VisitAsia = Variable('Visit_To_Asia', ['visit', 'no-visit'])
     F1 = Factor("F1", [VisitAsia])
     F1.add_values([['visit', 0.01], ['no-visit', 0.99]])

     Smoking = Variable('Smoking', ['smoker', 'non-smoker'])
     F2 = Factor("F2", [Smoking])
     F2.add_values([['smoker', 0.5], ['non-smoker', 0.5]])

     Tuberculosis = Variable('Tuberculosis', ['present', 'absent'])
     F3 = Factor("F3", [Tuberculosis, VisitAsia])
     F3.add_values([['present', 'visit', 0.05],
                    ['present', 'no-visit', 0.01],
                    ['absent', 'visit', 0.95],
                    ['absent', 'no-visit', 0.99]])

     Cancer = Variable('Lung Cancer', ['present', 'absent'])
     F4 = Factor("F4", [Cancer, Smoking])
     F4.add_values([['present', 'smoker', 0.10],
                    ['present', 'non-smoker', 0.01],
                    ['absent', 'smoker', 0.90],
                    ['absent', 'non-smoker', 0.99]])

     Bronchitis = Variable('Bronchitis', ['present', 'absent'])
     F5 = Factor("F5", [Bronchitis, Smoking])
     F5.add_values([['present', 'smoker', 0.60],
                    ['present', 'non-smoker', 0.30],
                    ['absent', 'smoker', 0.40],
                    ['absent', 'non-smoker', 0.70]])

     TBorCA = Variable('Tuberculosis or Lung Cancer', ['true', 'false'])
     F6 = Factor("F6", [TBorCA, Tuberculosis, Cancer])
     F6.add_values([['true', 'present', 'present', 1.0],
                    ['true', 'present', 'absent', 1.0],
                    ['true', 'absent', 'present', 1.0],
                    ['true', 'absent', 'absent', 0],
                    ['false', 'present', 'present', 0],
                    ['false', 'present', 'absent', 0],
                    ['false', 'absent', 'present', 0],
                    ['false', 'absent', 'absent', 1]])


     Dyspnea = Variable('Dyspnea', ['present', 'absent'])
     F7 = Factor("F7", [Dyspnea, TBorCA, Bronchitis])
     F7.add_values([['present', 'true', 'present', 0.9],
                    ['present', 'true', 'absent', 0.7],
                    ['present', 'false', 'present', 0.8],
                    ['present', 'false', 'absent', 0.1],
                    ['absent', 'true', 'present', 0.1],
                    ['absent', 'true', 'absent', 0.3],
                    ['absent', 'false', 'present', 0.2],
                    ['absent', 'false', 'absent', 0.9]])


     Xray = Variable('XRay Result', ['abnormal', 'normal'])
     F8 = Factor("F8", [Xray, TBorCA])
     F8.add_values([['abnormal', 'true', 0.98],
                    ['abnormal', 'false', 0.05],
                    ['normal', 'true', 0.02],
                    ['normal', 'false', 0.95]])

     Asia = BN("Asia", [VisitAsia, Smoking, Tuberculosis, Cancer,
                        Bronchitis, TBorCA, Dyspnea, Xray],
                        [F1, F2, F3, F4, F5, F6, F7, F8])

     return [Asia, VisitAsia, Smoking, Tuberculosis, Cancer,
                        Bronchitis, TBorCA, Dyspnea, Xray, F1, F2, F3, F4, F5, F6, F7, F8]

def makeQ3():

     ## E,B,S,w,G example from sample questions
     E = Variable('E', ['e', '-e'])
     B = Variable('B', ['b', '-b'])
     S = Variable('S', ['s', '-s'])
     G = Variable('G', ['g', '-g'])
     W = Variable('W', ['w', '-w'])
     FE = Factor('P(E)', [E])
     FB = Factor('P(B)', [B])
     FS = Factor('P(S|E,B)', [S, E, B])
     FG = Factor('P(G|S)', [G,S])
     FW = Factor('P(W|S)', [W,S])

     FE.add_values([['e',0.1], ['-e', 0.9]])
     FB.add_values([['b', 0.1], ['-b', 0.9]])
     FS.add_values([['s', 'e', 'b', .9], ['s', 'e', '-b', .2], ['s', '-e', 'b', .8],['s', '-e', '-b', 0],
                    ['-s', 'e', 'b', .1], ['-s', 'e', '-b', .8], ['-s', '-e', 'b', .2],['-s', '-e', '-b', 1]])
     FG.add_values([['g', 's', 0.5], ['g', '-s', 0], ['-g', 's', 0.5], ['-g', '-s', 1]])
     FW.add_values([['w', 's', 0.8], ['w', '-s', .2], ['-w', 's', 0.2], ['-w', '-s', 0.8]])

     Q3 = BN('SampleQ4', [E,B,S,G,W], [FE,FB,FS,FG,FW])
     return [Q3,E,B,S,G,W,FE,FB,FS,FG,FW]

# ORDERING Tests
def min_fill_ordering_TA(Factors, QueryVar):
    '''Compute a min fill ordering given a list of factors. Return a list
    of variables from the scopes of the factors in Factors. The QueryVar is
    NOT part of the returned ordering'''
    scopes = []
    for f in Factors:
        scopes.append(list(f.get_scope()))
    Vars = []
    for s in scopes:
        for v in s:
            if not v in Vars and v != QueryVar:
                Vars.append(v)

    ordering = []
    while Vars:
        (var, new_scope) = min_fill_var(scopes, Vars)
        ordering.append(var)
        if var in Vars:
            Vars.remove(var)
        scopes = remove_var(var, new_scope, scopes)
    return ordering


def min_fill_var(scopes, Vars):
    '''Given a set of scopes (lists of lists of variables) compute and
    return the variable with minimum fill in. That the variable that
    generates a factor of smallest scope when eliminated from the set
    of scopes. Also return the new scope generated from eliminating
    that variable.'''
    minv = Vars[0]
    (minfill, min_new_scope) = compute_fill(scopes, Vars[0])
    for v in Vars[1:]:
        (fill, new_scope) = compute_fill(scopes, v)
        if fill < minfill:
            minv = v
            minfill = fill
            min_new_scope = new_scope
    return (minv, min_new_scope)


def compute_fill(scopes, var):
    '''Return the fill in scope generated by eliminating var from
    scopes along with the size of this new scope'''
    union = []
    for s in scopes:
        if var in s:
            for v in s:
                if not v in union:
                    union.append(v)
    if var in union: union.remove(var)
    return (len(union), union)


def remove_var(var, new_scope, scopes):
    '''Return the new set of scopes that arise from eliminating var
    from scopes'''
    new_scopes = []
    for s in scopes:
        if not var in s:
            new_scopes.append(s)
    new_scopes.append(new_scope)
    return new_scopes


# NB TESTS (worth 20)
def nb_test_1(student_modules):
    details = set()
    score = 0

    nb = NaiveBayesModel()
    prior_count = 0
    for f in nb.Factors:
        s = f.scope
        if (len(s) == 1): prior_count += 1
        if (len(s) > 2):
            score -= 1
            details.add("Model is NOT a Naive Bayes Model.")

    if prior_count > 1:
        score -= 1
        details.add("Model is NOT a Naive Bayes Model.")

    if score == 0:
        details.add("Model is structured like a Naive Bayes Model.")
        score = 10
    else:
        score = 0

    details.add("nb_test_1:  {}".format(score))
    return score, details


def nb_test_2(student_modules):
    details = set()
    score = 0
    scopes = {}

    model = NaiveBayesModel()
    for f in model.Factors:
        if len(f.get_scope()) == 1:
            if (f.sum_table() == 1):
                score += 2
            else:
                details.add("Values in table with scope {} don't reflect probabilities.".format(f.get_scope()))

        if len(f.get_scope()) == 2:
            if str(f.get_scope()) not in scopes.keys():
                scopes[str(f.get_scope())] = f.sum_table()
            else:
                scopes[str(f.get_scope())] = f.sum_table() + scopes[str(f.get_scope())]

    for key in scopes.keys():
        if (abs(scopes[key] - 2) < 0.02):
            score += 1
        else:
            details.add("Values in table with scope {} don't collectively sum to 2.".format(key))

    details.add("nb_test_2:  {}".format(score))
    return score, details


# MINFILL TEST (worth 7)
def minfill_test_1(student_modules):
    details = set()
    score = 0
    min_fill_ordering = getattr(student_modules, "min_fill_ordering")

    myBN = adultDatasetBN()

    # ordering = min_fill_ordering_TA(myBN.factors(),myBN.variables()[0])
    # print(ordering)
    ordering2 = min_fill_ordering(myBN.factors(), myBN.variables()[0])

    if (ordering2[0].name == 'Work' or ordering2[0].name == 'Country'):
        score = 3
    else:
        details.add("Min fill choice of variable should be Work or Country")

        # print(ordering2)
    # details.add(model)

    details.add("minfill_test_1:  {}".format(score))
    # details = "\n".join(details)
    return score, details


# @max_grade(2)
def minfill_test_2(student_modules):
    details = set()
    min_fill_ordering = getattr(student_modules, "min_fill_ordering")

    score = 0

    myBN = adultDatasetBN2()

    # ordering = min_fill_ordering_TA(myBN.factors(),myBN.variables()[5])
    # print(ordering)
    ordering2 = min_fill_ordering(myBN.factors(), myBN.variables()[5])

    if (ordering2[0].name == 'Race'):
        score = 4
    else:
        details.add("Min fill choice of variable should be Work or Country")

        # print(ordering2)
    # details.add(model)

    details.add("minfill_test_2: {}".format(score))
    # details = "\n".join(details)
    return score, details


# PROBLEM TEST (worth 7)
def problem_test_1(student_modules):
    details = set()
    score = 0
    stu_solution = student_modules[SOLUTION]

    myBN = stu_solution.NaiveBayesModel()
    sol = [100, 0.0, 4.6, 16.9, 8.1, 25.4]

    # What percentage of the women in the test data set end up with a P(S=">=$50K"|E1) that is strictly greater than P(S=">=$50K"|E2)?
    # What percentage of the men in the test data set end up with a P(S=">=$50K"|E1) that is strictly greater than P(S=">=$50K"|E2)?
    # What percentage of the women in the test data set with P(S=">=$50K"|E1) > 0.5 actually have a salary over $50K?
    # What percentage of the men in the test data set with P(S=">=$50K"|E1) > 0.5 actually have a salary over $50K?
    # What percentage of the women in the test data set are assigned a P(Salary=">=$50K"|E1) > 0.5, overall?
    # What percentage of the men in the test data set are assigned a P(Salary=">=$50K"|E1) > 0.5, overall?
    wiggle = 3
    if ('Explore' in dir(stu_solution)):

        ans1 = Explore(myBN, 1)
        if (abs(ans1 - sol[0]) < wiggle):
            score += 2
        ans2 = Explore(myBN, 2)
        if (abs(ans2 - sol[1]) < wiggle):
            score += 2
        if (ans1 > ans2):
            score += 2
        ans3 = Explore(myBN, 3)
        if (abs(ans3 - sol[2]) < wiggle):
            score += 2
        ans4 = Explore(myBN, 4)
        if (abs(ans4 - sol[3]) < wiggle):
            score += 2
        if (ans3 < ans4):
            score += 2
        ans5 = Explore(myBN, 5)
        if (abs(ans5 - sol[4]) < wiggle):
            score += 3
        ans6 = Explore(myBN, 6)
        if (abs(ans6 - sol[5]) < wiggle):
            score += 3
        if (ans5 < ans6):
            score += 2

        details.add("problem_test_1:  {}".format(score))

    elif ('explore' in dir(stu_solution)):

        ans1 = explore(myBN, 1)
        if (abs(ans1 - sol[0]) < wiggle):
            score += 2
        ans2 = explore(myBN, 2)
        if (abs(ans2 - sol[1]) < wiggle):
            score += 2
        if (ans1 > ans2):
            score += 2
        ans3 = explore(myBN, 3)
        if (abs(ans3 - sol[2]) < wiggle):
            score += 2
        ans4 = explore(myBN, 4)
        if (abs(ans4 - sol[3]) < wiggle):
            score += 2
        if (ans3 < ans4):
            score += 2
        ans5 = explore(myBN, 5)
        if (abs(ans5 - sol[4]) < wiggle):
            score += 3
        ans6 = explore(myBN, 6)
        if (abs(ans6 - sol[5]) < wiggle):
            score += 3
        if (ans5 < ans6):
            score += 2

        details.add("problem_test_1:  {}".format(score))

    return score, details


def create_test_results(name, output, marks_earned, marks_total):
    """Return a JSON string"""

    status = "pass" if marks_earned >= marks_total else "partial" if marks_earned > 0 else "fail"
    if marks_total == 0:
        status = 'fail'

    results = {"name": name,
               "output": output,
               "marks_earned": marks_earned,
               "marks_total": marks_total,
               "status": status
               }
    return results


def create_test_results_short(name, output, marks_earned, marks_total):
    """Return a JSON string"""

    status = "pass" if marks_earned >= marks_total else "partial" if marks_earned > 0 else "fail"
    if marks_total == 0:
        status = 'fail'

    results = {"name": name,
               # "output": output,
               "marks_earned": marks_earned,
               "marks_total": marks_total,
               "status": status
               }
    return results


# VE TESTS (worth 25) 14+11 = 25
def ve_test_1(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

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
        print(Smoking)
        print(Bronchitis)
        print(Asia)
        probs = VE(Asia, Bronchitis, [Smoking])
        if abs(probs[0] - 0.6) < 0.002 and abs(probs[1] - 0.4) < 0.002:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(Bronchitis=present|Smoking=smoker) = {} P(Bronchitis=absent|Smoking=smoker) = {}'.format(probs[0],
                                                                                                        probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_1: ".format(score))
    details = "\n".join(details)
    return 2 * score, details


def ve_test_2(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeBN()

    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Dyspnea = Parameters[7]
    Tuberculosis = Parameters[3]

    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("VE Test 2 ....")
        Tuberculosis.set_evidence('present')
        probs = VE(Asia, Dyspnea, [Tuberculosis])
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
    return 2 * score, details


def ve_test_3(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Dyspnea = Parameters[7]
    TBorCA = Parameters[6]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("VE Test 3 ....")
        TBorCA.set_evidence('true')
        probs = VE(Asia, Dyspnea, [TBorCA])
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
    return 2 * score, details


def ve_test_4(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
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
        probs = VE(Asia, TBorCA, [VisitAsia, Smoking])
        if abs(probs[0] - 0.145) < 0.002 and abs(probs[1] - 0.855) < 0.002:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(TBorC=true|Smoking=smoker,VisitAsia=visit) = {} P(TBorC=false|Smoking=smoker,VisitAsia=visit) = {}'.format(
                probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_4: ".format(score))
    details = "\n".join(details)
    return 2 * score, details


def ve_test_5(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
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
        probs = VE(Asia, TBorCA, [Xray])
        if abs(probs[0] - 0.5760396859045477) < 0.002 and abs(probs[1] - 0.4239603140954523) < 0.002:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(TBorC=true|Xray=abnormal,VisitAsia=visit) = {} P(TBorC=false|Xray=abnormal,VisitAsia=visit) = {}'.format(
                probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_5: ".format(score))
    details = "\n".join(details)
    return 2 * score, details

def ve_test_6(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Cancer = Parameters[4]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("VE Test 6 ....")
        probs = VE(Asia, Cancer, [])
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
    return 2 * score, details

def ve_test_7(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1, F2, F3, F4, F5, F6, F7, F8]
    Asia = Parameters[0]
    Smoking = Parameters[2]
    Dyspnea = Parameters[7]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)

        details.add("VE Test 7 ....")
        Dyspnea.set_evidence('present')
        probs1 = VE(Asia, Smoking, [Dyspnea])
        Dyspnea.set_evidence('absent')
        probs2 = VE(Asia, Smoking, [Dyspnea])
        if abs(probs1[0] - 0.6339) < 0.0001 and abs(probs1[1] - 0.366) < 0.0001 and abs(
                probs2[0] - 0.3964) < 0.0001 and abs(probs2[1] - 0.60357) < 0.0001:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(Smoking=smoker|Dyspnea=present) = {} P(Smoking=non-smoker|Dyspnea=present) = {} P(Smoking=smoker|Dyspnea=absent) = {} P(Smoking=non-smoker|Dyspnea=absent) = {}'.format(
                probs1[0], probs1[1], probs2[0], probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("ve_test_7: ".format(score))
    details = "\n".join(details)
    return 2 * score, details

def ve_test_8(student_modules):
    score = 0
    VE = getattr(student_modules, "VE")

    details = set()

    Parameters = makeQ3()
    # [Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
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
        probs = VE(Q3, S, [G])
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

    # (b)
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("OVE Test 2 ....")
        B.set_evidence('b')
        E.set_evidence('-e')
        probs = VE(Q3, W, [B, E])
        if abs(probs[0] - 0.68) < 0.0001 and abs(probs[1] - 0.32) < 0.0001:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")

        details.add('P(w|b,-e) = {} P(-w|b,-e) = {}'.format(probs[0], probs[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    # (c)
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("OVE Test 3 ....")
        S.set_evidence('s')
        probs1 = VE(Q3, G, [S])
        S.set_evidence('-s')
        probs2 = VE(Q3, G, [S])
        if probs1[0] == 0.5 and probs1[1] == 0.5 and probs2[0] == 0.0 and probs2[1] == 1.0:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(g|s) = {} P(-g|s) = {} P(g|-s) = {} P(-g|-s) = {}'.format(probs1[0], probs1[1], probs2[0], probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    # (d)
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("OVE Test 4 ....")
        S.set_evidence('s')
        W.set_evidence('w')
        probs1 = VE(Q3, G, [S, W])
        S.set_evidence('s')
        W.set_evidence('-w')
        probs2 = VE(Q3, G, [S, W])
        if probs1[0] == 0.5 and probs1[1] == 0.5 and probs2[0] == 0.5 and probs2[1] == 0.5:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(g|s,w) = {} P(-g|s,w) = {} P(g|s,-w) = {} P(-g|s,-w) = {}'.format(probs1[0], probs1[1], probs2[0],
                                                                                 probs2[1]))
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
        probs3 = VE(Q3, G, [S, W])
        S.set_evidence('-s')
        W.set_evidence('-w')
        probs4 = VE(Q3, G, [S, W])
        if probs3[0] == 0.0 and probs3[1] == 1.0 and probs4[0] == 0.0 and probs4[1] == 1.0:
            score += 2
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(g|-s,w) = {} P(-g|-s,w) = {} P(g|-s,-w) = {} P(-g|-s,-w) = {}'.format(probs3[0], probs3[1], probs4[0],
                                                                                     probs4[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    # (f)
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("OVE Test 6 ....")
        W.set_evidence('w')
        probs1 = VE(Q3, G, [W])
        W.set_evidence('-w')
        probs2 = VE(Q3, G, [W])
        if abs(probs1[0] - 0.15265998457979954) < 0.0001 and abs(probs1[1] - 0.8473400154202004) < 0.0001 and abs(
                probs2[0] - 0.01336753983256819) < 0.0001 and abs(probs2[1] - 0.9866324601674318) < 0.0001:
            score += 2
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(g|w) = {} P(-g|w) = {} P(g|-w) = {} P(-g|-w) = {}'.format(probs1[0], probs1[1], probs2[0], probs2[1]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    # (h)
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("OVE Test 7 ....")
        probs = VE(Q3, G, [])
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
        probs = VE(Q3, E, [])
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


# NORMALIZATION TESTS (WORTH 7)
def norm_test_1(student_modules):
    score = 0
    normalize = getattr(student_modules, "normalize")

    details = set()

    details.add("Normalization test 1 ....")
    normalized_nums = normalize([i for i in range(5)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
        details.add("passed.")
        score += 3
    else:
        details.add("failed.")
    details.add('{} when normalized to {} sum to {}'.format([i for i in range(5)], normalized_nums, norm_sum))

    return score, details

def norm_test_2(student_modules):
    score = 0
    normalize = getattr(student_modules, "normalize")

    details = set()

    details.add("Normalization test 2 ....")
    normalized_nums = normalize([i for i in range(0, -5, -1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
        details.add("passed.")
        score += 2
    else:
        details.add("failed.")
    details.add('Input when normalized to {} sum to {}'.format(normalized_nums, norm_sum))

    return score, details


def norm_test_3(student_modules):
    score = 0
    normalize = getattr(student_modules, "normalize")
    details = set()

    details.add("Normalization test 4 ....")
    normalized_nums = normalize([i for i in range(0, -5, -1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
        details.add("passed.")
        score += 2
    else:
        details.add("failed.")
    details.add('Input when normalized to {} sum to {}'.format(normalized_nums, norm_sum))
    return score, details


# MULTIPLY FACTORS TESTS  (WORTH 7)
def multiply_factors_test_1(student_modules):
    score = 0
    multiply_factors = getattr(student_modules, "multiply_factors")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    F2 = Parameters[10]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("MF Test 1 ....")
        factor = multiply_factors([F2])
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


def multiply_factors_test_2(student_modules):
    score = 0
    multiply_factors = getattr(student_modules, "multiply_factors")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    F1 = Parameters[9]
    F2 = Parameters[10]
    VisitAsia = Parameters[1]
    Smoking = Parameters[2]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("MF Test 2 ....")
        factor = multiply_factors([F1, F2])
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
        if abs(values[0] - 0.005) < 0.002 and abs(values[1] - 0.005) < 0.002 and abs(values[2] - 0.495) < 0.002 and abs(
                values[3] - 0.495) < 0.002:
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")

        details.add(
            'P(visit,smoker) = {} P(no-visit,smoker) = {} P(visit,non-smoker) = {} P(no-visit,non-smoker) = {}'.format(
                values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("multiply_factors_test_2: ".format(score))
    details = "\n".join(details)
    return score, details


def multiply_factors_test_3(student_modules):
    score = 0
    multiply_factors = getattr(student_modules, "multiply_factors")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    VisitAsia = Parameters[1]
    Bronchitis = Parameters[5]
    Smoking = Parameters[2]
    F1 = Parameters[9]
    F5 = Parameters[13]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("MF Test 3 ....")
        factor = multiply_factors([F1, F5])
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
    return 2 * score, details


def multiply_factors_test_4(student_modules):
    score = 0
    multiply_factors = getattr(student_modules, "multiply_factors")
    details = set()

    Parameters = makeQ3()
    # [Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
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
        factor = multiply_factors([FE])
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
        factor = multiply_factors([FB, FE])
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
                tests.append(value == FE.get_value([e_val]) * FB.get_value([b_val]))
        if all(tests):
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(e,b) = {} P(-e,b) = {} P(e,-b) = {} P(-e,-b) = {}'.format(values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("OMF Test 3 ....")
        factor = multiply_factors([FE, FS])
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
                tests.append(value == FE.get_value([e_val]) * FS.get_value([s_val, e_val, b_val]))
        if all(tests):
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(e,s,b) = {} P(-e,s,b) = {} P(e,-s,-b) = {} P(-e,s,-b) = {}'.format(values[0], values[1], values[2],
                                                                                  values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("multiply_factors_test_4: ".format(score))
    details = "\n".join(details)
    return score, details


# RESTRICT FACTORS TESTS  (WORTH 7)
def restrict_factor_test_1(student_modules):
    score = 0
    restrict_factor = getattr(student_modules, "restrict_factor")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    VisitAsia = Parameters[1]
    F1 = Parameters[9]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("\nRestrict Factor Tests")
        details.add("RF Test 1 ....")
        factor = restrict_factor(F1, VisitAsia, 'visit')
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


def restrict_factor_test_2(student_modules):
    score = 0
    restrict_factor = getattr(student_modules, "restrict_factor")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    Smoking = Parameters[2]
    Bronchitis = Parameters[5]
    F5 = Parameters[13]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("RF Test 2 ....")
        factor = restrict_factor(F5, Smoking, 'non-smoker')
        factor = restrict_factor(factor, Bronchitis, 'absent')
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


def restrict_factor_test_3(student_modules):
    score = 0
    restrict_factor = getattr(student_modules, "restrict_factor")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6 14, F7 15, F8]
    TBorCA = Parameters[6]
    Bronchitis = Parameters[5]
    Dyspnea = Parameters[7]
    F7 = Parameters[15]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("RF Test 3 ....")
        factor = restrict_factor(F7, Dyspnea, 'absent')
        factor = restrict_factor(factor, TBorCA, 'true')
        factor = restrict_factor(factor, Bronchitis, 'present')
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
    return 2 * score, details


def restrict_factor_test_4(student_modules):
    score = 0
    restrict_factor = getattr(student_modules, "restrict_factor")
    details = set()

    Parameters = makeQ3()
    # [Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
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
        factor = restrict_factor(FE, E, 'e')
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
        factor = restrict_factor(FG, S, '-s')
        factor = restrict_factor(factor, G, '-g')
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
        factor = restrict_factor(FS, S, '-s')
        factor = restrict_factor(factor, E, '-e')
        factor = restrict_factor(factor, B, 'b')
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

def sum_out_variable_test_1(student_modules):
    score = 0
    sum_out_variable = getattr(student_modules,"sum_out_variable")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    VisitAsia = Parameters[1]
    F1 = Parameters[9]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("SOV Test 1 ....")
        factor = sum_out_variable(F1, VisitAsia)
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
    return 2 * score, details


# SUM FACTORS TESTS  (WORTH 7)
def sum_out_variable_test_2(student_modules):
    score = 0
    sum_out_variable = getattr(student_modules,"sum_out_variable")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6, F7, F8]
    Smoking = Parameters[2]
    F4 = Parameters[12]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("SOV Test 2 ....")
        factor = sum_out_variable(F4, Smoking)
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
    return 2 * score, details


def sum_out_variable_test_3(student_modules):
    score = 0
    sum_out_variable = getattr(student_modules,"sum_out_variable")
    details = set()

    Parameters = makeBN()
    # [Asia 0, VisitAsia 1, Smoking 2, Tuberculosis 3, Cancer 4, Bronchitis 5, TBorCA 6, Dyspnea 7, Xray 8, F1 9, F2 10, F3 11, F4 12, F5 13, F6 14, F7, F8]
    Tuberculosis = Parameters[3]
    Cancer = Parameters[4]
    F6 = Parameters[14]
    try:
        timeout = DEFAULT_TIMEOUT
        setTO(timeout)
        details.add("SOV Test 3 ....")
        factor1 = sum_out_variable(F6, Tuberculosis)
        factor2 = sum_out_variable(factor1, Cancer)
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

def sum_out_variable_test_4(student_modules):
    score = 0
    sum_out_variable = getattr(student_modules,"sum_out_variable")
    details = set()

    Parameters = makeQ3()
    # [Q3,E,B,S,G,W,FE,FB,FS,FG,FW]
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
        factor = sum_out_variable(FE, E)
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
        factor = sum_out_variable(FS, E)
        values = (factor.get_value(["s", "b"]), factor.get_value(["s", "-b"]), factor.get_value(["-s", "b"]),
                  factor.get_value(["-s", "-b"]))
        tests = (abs(values[0] - 1.7) < 0.002, abs(values[1] - 0.2) < 0.002, abs(values[2] - 0.3) < 0.002,
                 abs(values[3] - 1.8) < 0.002)
        if all(tests):
            score += 1
            details.add("passed.")
        else:
            details.add("failed.")
        details.add(
            'P(S = s | B = b) = {} P(S = s | B = -b) = {} P(S = -s | B = b) = {} P(S = -s | B = -b) = {}'.format(
                values[0], values[1], values[2], values[3]))
    except TO_exc:
        details.add("Got TIMEOUT")
    except:
        details.add("A runtime error occurred: %r" % traceback.format_exc())

    details.add("sum_out_variable_test_4: ".format(score))
    details = "\n".join(details)
    return score, details


if __name__ == '__main__':
    import json

    #args = sys.argv
    #name = args[1]
    #student = args[2]

    name = "all"
    student = "test"

    # import student's functions
    try:
        #module1_name = "students." + student + ".A4.solution"
        module1_name = "solution"
        module1 = importlib.import_module(module1_name)
        FOUND_SOLUTION = True
    except Exception:
        FOUND_SOLUTION = False
        IMPORT_ERROR = traceback.format_exc()

    if FOUND_SOLUTION is False:
        filename = student + "_results.txt"
        f = open(filename, "w")
        f.write(json.dumps(create_test_results("error", f"Could not import solution. {IMPORT_ERROR}", 0, 0)))
        f.close()
        exit()

    test_groups = {
        "test_ve": [ve_test_1, ve_test_2, ve_test_3, ve_test_4, ve_test_5, ve_test_6, ve_test_7, ve_test_8],
        "test_multiply": [multiply_factors_test_1,multiply_factors_test_2,multiply_factors_test_3,multiply_factors_test_4],
        "test_restrict": [restrict_factor_test_1, restrict_factor_test_2, restrict_factor_test_3, restrict_factor_test_4],
        "test_normalize": [norm_test_1, norm_test_2, norm_test_3],
        "test_sum": [sum_out_variable_test_1, sum_out_variable_test_2,sum_out_variable_test_3,sum_out_variable_test_4],
        "test_minfill": [minfill_test_1, minfill_test_2],
        #"test_nb": [nb_test_1, nb_test_2],
        #"test_problem": [problem_test_1],
        "all": [minfill_test_1, minfill_test_2, sum_out_variable_test_1, sum_out_variable_test_2,sum_out_variable_test_3,sum_out_variable_test_4,
                norm_test_1, norm_test_2, norm_test_3, restrict_factor_test_1, restrict_factor_test_2, restrict_factor_test_3, restrict_factor_test_4,
                multiply_factors_test_1,multiply_factors_test_2,multiply_factors_test_3,multiply_factors_test_4,
                ve_test_1, ve_test_2, ve_test_3, ve_test_4, ve_test_5, ve_test_6, ve_test_7, ve_test_8]
    }

    test_case_weight = {
        ve_test_1: 2,
        ve_test_2: 2,
        ve_test_3: 2,
        ve_test_4: 2,
        ve_test_5: 2,
        ve_test_6: 2,
        ve_test_7: 2,
        ve_test_8: 11,
        multiply_factors_test_1: 1,
        multiply_factors_test_2: 1,
        multiply_factors_test_3: 2,
        multiply_factors_test_4: 3,
        restrict_factor_test_1: 1,
        restrict_factor_test_2: 1,
        restrict_factor_test_3: 2,
        restrict_factor_test_4: 3,
        norm_test_1: 3,
        norm_test_2: 2,
        norm_test_3: 2,
        sum_out_variable_test_1: 2,
        sum_out_variable_test_2: 2,
        sum_out_variable_test_3: 1,
        sum_out_variable_test_4: 2,
        minfill_test_1: 3,
        minfill_test_2: 4
    }

    filename = student + "_results.txt"
    f = open(filename, "w")
    f.close()

    gradefile = "A4.csv"
    g = open(gradefile, "a")

    filename = student + "_results.txt"
    f = open(filename, "a")
    results = []
    other = []
    for test in test_groups[name]:
        test_case_name = test.__name__
        weight = test_case_weight[test]
        try:
            score, details = test(module1)
            results.append(create_test_results(test_case_name,
                                               details,
                                               score, weight))
            other.append(create_test_results_short(test_case_name,
                                                   details,
                                                   score, weight))
        except Exception:
            results.append(create_test_results(test_case_name,
                                               traceback.format_exc(),
                                               0, weight))
            other.append(create_test_results_short(test_case_name,
                                                   traceback.format_exc(),
                                                   0, weight))
    total = 0
    g.write("{},".format(student))
    arr = []
    for item in results:
        f.write("***********************\n")
        f.write("Test: {}\n".format(item['name']))
        f.write("{}\n".format(item['output']))
        f.write("SCORE: {}/{}\n".format(item['marks_earned'], item['marks_total'], ))
        arr.append(item['marks_earned'])
        if item == results[-1]:
            g.write("{}".format(item['marks_earned']))
        else:
            g.write("{},".format(item['marks_earned']))
        total += int(item['marks_earned'])
        f.write("***********************\n")

    g.write("\n")
    f.write("\n\n***********************\n")
    f.write("TOTAL: {}\n".format(total))
    f.write("***********************\n")
    f.close()