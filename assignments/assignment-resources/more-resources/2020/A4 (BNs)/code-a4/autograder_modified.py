##Three sample bayes nets are defined here. ##
from bnetbase_solved import *

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

if __name__ == '__main__':
    # Unseen VE tests
    print("\nVE Tests")
    print("Test 1 ....", end = '')
    Smoking.set_evidence('smoker')
    probs = VE(Asia, Bronchitis, [Smoking])
    if abs(probs[0] - 0.6) < 0.001 and abs(probs[1] - 0.4) < 0.001:
      print("passed.")
    else:
      print("failed.")
    print('P(Bronchitis=present|Smoking=smoker) = {} P(Bronchitis=absent|Smoking=smoker) = {}'.format(probs[0], probs[1]))

    print("Test 2 ....", end = '')
    Tuberculosis.set_evidence('present')
    probs = VE(Asia, Dyspnea, [Tuberculosis])
    if abs(probs[0] - 0.789) < 0.001 and probs[1] == 0.21:
      print("passed.")
    else:
      print("failed.")
    print('P(Xray=normal|TBorCA=true) = {} P(Xray=abnormal|TBorCA=true) = {}'.format(probs[0], probs[1]))

    print("Test 3 ....", end = '')
    TBorCA.set_evidence('true')
    probs = VE(Asia, Dyspnea, [TBorCA])
    if abs(probs[0] - 0.8106077620781144) < 0.001 and abs(probs[1] - 0.1893922379218856) < 0.001:
      print("passed.")
    else:
      print("failed.")
    print('P(Dyspnea=present|TBorCA=true) = {} P(Dyspnea=absent|TBorCA=true) = {}'.format(probs[0], probs[1]))

    print("Test 4 ....", end = '')
    Smoking.set_evidence('smoker')
    VisitAsia.set_evidence('visit')
    probs = VE(Asia, TBorCA, [VisitAsia, Smoking])
    if abs(probs[0] - 0.145) < 0.001 and abs(probs[1] - 0.855) < 0.001:
      print("passed.")
    else:
      print("failed.")
    print('P(TBorC=true|Smoking=smoker,VisitAsia=visit) = {} P(TBorC=false|Smoking=smoker,VisitAsia=visit) = {}'.format(probs[0], probs[1]))
     
    print("Test 5 ....", end = '')
    Xray.set_evidence('abnormal')
    VisitAsia.set_evidence('visit')
    probs = VE(Asia, TBorCA, [Xray])
    if abs(probs[0] - 0.5760396859045477) < 0.001 and abs(probs[1] - 0.4239603140954523) < 0.001:
      print("passed.")
    else:
      print("failed.")
    print('P(TBorC=true|Xray=abnormal,VisitAsia=visit) = {} P(TBorC=false|Xray=abnormal,VisitAsia=visit) = {}'.format(probs[0], probs[1]))

    print("Test 6 ....", end = '')
    probs = VE(Asia, Cancer, [])
    if abs(probs[0] - 0.055) < 0.001 and abs(probs[1] - 0.945) < 0.001:
      print("passed.")
    else:
      print("failed.")
    print('P(Cancer=present) = {} P(Cancer=absent) = {}'.format(probs[0], probs[1]))

    print("Test 7 ....", end = '')
    Dyspnea.set_evidence('present')
    probs1 = VE(Asia, Smoking, [Dyspnea])
    Dyspnea.set_evidence('absent')
    probs2 = VE(Asia, Smoking, [Dyspnea])
    if abs(probs1[0] - 0.6339) < 0.0001 and abs(probs1[1] - 0.366) < 0.0001 and abs(probs2[0] - 0.3964) < 0.0001 and abs(probs2[1] - 0.60357) < 0.0001:
      print("passed.")
    else:
      print("failed.")      
    print('P(Smoking=smoker|Dyspnea=present) = {} P(Smoking=non-smoker|Dyspnea=present) = {} P(Smoking=smoker|Dyspnea=absent) = {} P(Smoking=non-smoker|Dyspnea=absent) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))

    # Unseen multiply_factors tests
    print("\nMultiply Factors Tests")
    print("Test 1 ....", end = '')    
    factor = multiply_factors([F2])
    values = (factor.get_value(['smoker']), factor.get_value(['non-smoker']))
    if values[0] == 0.5 and values[1] == 0.5:
      print("passed.")
    else:
      print("failed.")      
    print('P(smoker) = {} P(non-smoker) = {}'.format(values[0], values[1]))

    print("Test 2 ....", end = '')    
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
    if abs(values[0]-0.005) < 0.001 and abs(values[1]-0.005) < 0.001 and abs(values[2]-0.495) < 0.001 and abs(values[3]-0.495) < 0.001:
      print("passed.")
    else:
      print("failed.")      
    print('P(visit,smoker) = {} P(no-visit,smoker) = {} P(visit,non-smoker) = {} P(no-visit,non-smoker) = {}'.format(values[0], values[1], values[2], values[3]))

    print("Test 3 ....", end = '')    
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
    if all([abs(value - ev) < 0.001 for value, ev in zip(values, expected_values)]):
      print("passed.")
    else:
      print("failed.")      
    print('F1 x F5 = {}'.format(values))

    # Unseen restrict_factor tests
    print("\nRestrict Factor Tests")
    print("Test 1 ....", end = '')    
    factor = restrict_factor(F1, VisitAsia, 'visit')
    value = factor.get_value_at_current_assignments()
    if value == 0.01:
      print("passed.")
    else:
      print("failed.")
    print('P(VisitAsia=visit) = {}'.format(value))

    print("Test 2 ....", end = '')    
    factor = restrict_factor(F5, Smoking, 'non-smoker')
    factor = restrict_factor(factor, Bronchitis, 'absent')
    value = factor.get_value_at_current_assignments()
    if value == 0.7:
      print("passed.")
    else:
      print("failed.")
    print('P(Bronchitis=absent|Smoking=non-smoker) = {}'.format(value))

    print("Test 3 ....", end = '')    
    factor = restrict_factor(F7, Dyspnea, 'absent')
    factor = restrict_factor(factor, TBorCA, 'true')
    factor = restrict_factor(factor, Bronchitis, 'present')
    value = factor.get_value_at_current_assignments()
    if value == .1:
      print("passed.")
    else:
      print("failed.")
    print('P(Dyspnea=absent|TBorCA=true,Bronchitis=present) = {}'.format(value))

    # Unseen sum_out_variable tests
    print("\nSum Out Variable Tests")
    print("Test 1 ....", end = '')    
    factor = sum_out_variable(F1, VisitAsia)
    value = factor.get_value_at_current_assignments()
    if value == 1:
      print("passed.")
    else:
      print("failed.")
    print('sum P(VisitAsia) = {}'.format(value))
    
    print("Test 2 ....", end = '')    
    factor = sum_out_variable(F4, Smoking)
    values = (factor.get_value(["present"]), factor.get_value(["absent"]))
    tests = (abs(values[0] - 0.11) < 0.001, abs(values[1] - 1.89) < 0.001)
    if all(tests):
      print("passed.")
    else:
      print("failed.")
    print('P(Cancer = present) = {} P(Cancer = absent) = {} '.format(values[0], values[1]))

    print("Test 3 ....", end = '')    
    factor1 = sum_out_variable(F6, Tuberculosis)
    factor2 = sum_out_variable(factor1, Cancer)
    values = (factor2.get_value(["true"]), factor2.get_value(["false"]))
    tests = (abs(values[0] - 3.0) < 0.001, abs(values[1] - 1.0) < 0.001)
    if all(tests):
      print("passed.")
    else:
      print("failed.")
    print('P(TBorC = true) = {} P(TBorC = false) = {} '.format(values[0], values[1]))

    print("\nTests already seen by students")
    #(a)
    print("Test 1 ....", end = '')
    G.set_evidence('g')
    probs = VE(Q3, S, [G])
    if probs[0] == 1 and probs[1] == 0:
      print("passed.")
    else:
      print("failed.")
    
    print('P(s|g) = {} P(-s|g) = {}'.format(probs[0], probs[1]))

    #(b)
    print("Test 2 ....", end = '')
    B.set_evidence('b')
    E.set_evidence('-e')
    probs = VE(Q3, W, [B, E])
    if abs(probs[0] - 0.68) < 0.0001 and abs(probs[1] - 0.32) < 0.0001:
      print("passed.")
    else:
      print("failed.")    
    
    print('P(w|b,-e) = {} P(-w|b,-e) = {}'.format(probs[0],probs[1]))

    #(c)
    print("Test 3 ....", end = '')
    S.set_evidence('s')
    probs1 = VE(Q3, G, [S])
    S.set_evidence('-s')
    probs2 = VE(Q3, G, [S])
    if probs1[0] == 0.5 and probs1[1] == 0.5 and probs2[0] == 0.0 and probs2[1] == 1.0:
      print("passed.")
    else:
      print("failed.")  
    print('P(g|s) = {} P(-g|s) = {} P(g|-s) = {} P(-g|-s) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))

    #(d)
    print("Test 4 ....", end = '')
    S.set_evidence('s')
    W.set_evidence('w')
    probs1 = VE(Q3, G, [S,W])
    S.set_evidence('s')
    W.set_evidence('-w')
    probs2 = VE(Q3, G, [S,W])
    if probs1[0] == 0.5 and probs1[1] == 0.5 and probs2[0] == 0.5 and probs2[1] == 0.5:
      print("passed.")
    else:
      print("failed.")  
    print('P(g|s,w) = {} P(-g|s,w) = {} P(g|s,-w) = {} P(-g|s,-w) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))

    print("Test 5 ....", end = '')
    S.set_evidence('-s')
    W.set_evidence('w')
    probs3 = VE(Q3, G, [S,W])
    S.set_evidence('-s')
    W.set_evidence('-w')
    probs4 = VE(Q3, G, [S,W])
    if probs3[0] == 0.0 and probs3[1] == 1.0 and probs4[0] == 0.0 and probs4[1] == 1.0:
      print("passed.")
    else:
      print("failed.") 
    print('P(g|-s,w) = {} P(-g|-s,w) = {} P(g|-s,-w) = {} P(-g|-s,-w) = {}'.format(probs3[0],probs3[1],probs4[0],probs4[1]))

    #(f) 
    print("Test 6 ....", end = '')
    W.set_evidence('w')
    probs1 = VE(Q3, G, [W])
    W.set_evidence('-w')
    probs2 = VE(Q3, G, [W])
    if abs(probs1[0] - 0.15265998457979954) < 0.0001 and abs(probs1[1] - 0.8473400154202004) < 0.0001 and abs(probs2[0] - 0.01336753983256819) < 0.0001 and abs(probs2[1] - 0.9866324601674318) < 0.0001:
      print("passed.")
    else:
      print("failed.")      
    print('P(g|w) = {} P(-g|w) = {} P(g|-w) = {} P(-g|-w) = {}'.format(probs1[0],probs1[1],probs2[0],probs2[1]))

    #(h)
    print("Test 7 ....", end = '')
    probs = VE(Q3, G, [])
    if abs(probs[0] - 0.04950000000000001) < .0001 and abs(probs[1] - 0.9505) < .0001:
      print("passed.")
    else:
      print("failed.")      
    print('P(g) = {} P(-g) = {}'.format(probs[0], probs[1]))
    
    print("Test 8 ....", end = '')    
    probs = VE(Q3, E, [])
    if abs(probs[0] - 0.1) < 0.0001 and abs(probs[1] - 0.9) < 0.0001:
      print("passed.")
    else:
      print("failed.")      
    print('P(e) = {} P(-e) = {}'.format(probs[0], probs[1]))

    ## NEW TESTS ##
    print("\nMultiply Factors Tests")
    print("Test 1 ....", end = '')    
    factor = multiply_factors([FE])
    values = (factor.get_value(['e']), factor.get_value(['-e']))
    if values[0] == 0.1 and values[1] == 0.9:
      print("passed.")
    else:
      print("failed.")      
    print('P(e) = {} P(-e) = {}'.format(values[0], values[1]))

    print("Test 2 ....", end = '')    
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
        tests.append(value == FE.get_value([e_val])*FB.get_value([b_val]))
    if all(tests):
      print("passed.")
    else:
      print("failed.")      
    print('P(e,b) = {} P(-e,b) = {} P(e,-b) = {} P(-e,-b) = {}'.format(values[0], values[1], values[2], values[3]))

    print("Test 3 ....", end = '')    
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
        tests.append(value == FE.get_value([e_val])*FS.get_value([s_val, e_val, b_val]))
    if all(tests):
      print("passed.")
    else:
      print("failed.")      
    print('P(e,s,b) = {} P(-e,s,b) = {} P(e,-s,-b) = {} P(-e,s,-b) = {}'.format(values[0], values[1], values[2], values[3]))
    

    ##
    print("\nSum Out Variable Tests")
    print("Test 1 ....", end = '')    
    factor = sum_out_variable(FE, E)
    value = factor.get_value_at_current_assignments()
    if value == 1:
      print("passed.")
    else:
      print("failed.")
    print('sum_e P(e) = {}'.format(value))
    
    print("Test 2 ....", end = '')    
    factor = sum_out_variable(FS, E)
    values = (factor.get_value(["s", "b"]), factor.get_value(["s", "-b"]), factor.get_value(["-s", "b"]), factor.get_value(["-s", "-b"]))
    tests = (abs(values[0] - 1.7) < 0.001, abs(values[1] - 0.2) < 0.001, abs(values[2] - 0.3) < 0.001, abs(values[3] - 1.8) < 0.001)
    if all(tests):
      print("passed.")
    else:
      print("failed.")
    print('P(S = s | B = b) = {} P(S = s | B = -b) = {} P(S = -s | B = b) = {} P(S = -s | B = -b) = {}'.format(values[0], values[1], values[2], values[3]))

    ##
    print("\nRestrict Factor Tests")
    print("Test 1 ....", end = '')    
    factor = restrict_factor(FE, E, 'e')
    value = factor.get_value_at_current_assignments()
    if value == 0.1:
      print("passed.")
    else:
      print("failed.")
    print('P(E=e) = {}'.format(value))

    print("Test 2 ....", end = '')    
    factor = restrict_factor(FG, S, '-s')
    factor = restrict_factor(factor, G, '-g')
    value = factor.get_value_at_current_assignments()
    if value == 1:
      print("passed.")
    else:
      print("failed.")
    print('P(G=-g|S=s) = {}'.format(value))

    print("Test 3 ....", end = '')    
    factor = restrict_factor(FS, S, '-s')
    factor = restrict_factor(factor, E, '-e')
    factor = restrict_factor(factor, B, 'b')
    value = factor.get_value_at_current_assignments()
    if value == .2:
      print("passed.")
    else:
      print("failed.")
    print('P(S=-s|E=-e,B=b) = {}'.format(value))
    
    print("\nNormalize Tests")
    print("Test 1 ....", end = '')
    normalized_nums = normalize([i for i in range(5)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
      print("passed.")
    else:
      print("failed.")
    print('{} when normalized to {} sum to {}'.format([i for i in range(5)], normalized_nums, norm_sum))

    print("Test 2 ....", end = '')
    normalized_nums = normalize([i for i in range(0,-5,-1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 1:
      print("passed.")
    else:
      print("failed.")
    print('{} when normalized to {} sum to {}'.format([i for i in range(0,-5,-1)], normalized_nums, norm_sum))

    print("Test 3 ....", end = '')
    normalized_nums = normalize([i for i in range(4,-5,-1)])
    norm_sum = sum(normalized_nums)
    if norm_sum == 0:
      print("passed.")
    else:
      print("failed.")
    print('{} when normalized to {} sum to {}'.format([i for i in range(4,-5,-1)], normalized_nums, norm_sum))
