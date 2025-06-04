def makeBN(stu_solution):

     VisitAsia = stu_solution.Variable('Visit_To_Asia', ['visit', 'no-visit'])
     F1 = stu_solution.Factor("F1", [VisitAsia])
     F1.add_values([['visit', 0.01], ['no-visit', 0.99]])

     Smoking = stu_solution.Variable('Smoking', ['smoker', 'non-smoker'])
     F2 = stu_solution.Factor("F2", [Smoking])
     F2.add_values([['smoker', 0.5], ['non-smoker', 0.5]])

     Tuberculosis = stu_solution.Variable('Tuberculosis', ['present', 'absent'])
     F3 = stu_solution.Factor("F3", [Tuberculosis, VisitAsia])
     F3.add_values([['present', 'visit', 0.05],
                    ['present', 'no-visit', 0.01],
                    ['absent', 'visit', 0.95],
                    ['absent', 'no-visit', 0.99]])

     Cancer = stu_solution.Variable('Lung Cancer', ['present', 'absent'])
     F4 = stu_solution.Factor("F4", [Cancer, Smoking])
     F4.add_values([['present', 'smoker', 0.10],
                    ['present', 'non-smoker', 0.01],
                    ['absent', 'smoker', 0.90],
                    ['absent', 'non-smoker', 0.99]])

     Bronchitis = stu_solution.Variable('Bronchitis', ['present', 'absent'])
     F5 = stu_solution.Factor("F5", [Bronchitis, Smoking])
     F5.add_values([['present', 'smoker', 0.60],
                    ['present', 'non-smoker', 0.30],
                    ['absent', 'smoker', 0.40],
                    ['absent', 'non-smoker', 0.70]])

     TBorCA = stu_solution.Variable('Tuberculosis or Lung Cancer', ['true', 'false'])
     F6 = stu_solution.Factor("F6", [TBorCA, Tuberculosis, Cancer])
     F6.add_values([['true', 'present', 'present', 1.0],
                    ['true', 'present', 'absent', 1.0],
                    ['true', 'absent', 'present', 1.0],
                    ['true', 'absent', 'absent', 0],
                    ['false', 'present', 'present', 0],
                    ['false', 'present', 'absent', 0],
                    ['false', 'absent', 'present', 0],
                    ['false', 'absent', 'absent', 1]])


     Dyspnea = stu_solution.Variable('Dyspnea', ['present', 'absent'])
     F7 = stu_solution.Factor("F7", [Dyspnea, TBorCA, Bronchitis])
     F7.add_values([['present', 'true', 'present', 0.9],
                    ['present', 'true', 'absent', 0.7],
                    ['present', 'false', 'present', 0.8],
                    ['present', 'false', 'absent', 0.1],
                    ['absent', 'true', 'present', 0.1],
                    ['absent', 'true', 'absent', 0.3],
                    ['absent', 'false', 'present', 0.2],
                    ['absent', 'false', 'absent', 0.9]])


     Xray = stu_solution.Variable('XRay Result', ['abnormal', 'normal'])
     F8 = stu_solution.Factor("F8", [Xray, TBorCA])
     F8.add_values([['abnormal', 'true', 0.98],
                    ['abnormal', 'false', 0.05],
                    ['normal', 'true', 0.02],
                    ['normal', 'false', 0.95]])

     Asia = stu_solution.BN("Asia", [VisitAsia, Smoking, Tuberculosis, Cancer,
                        Bronchitis, TBorCA, Dyspnea, Xray],
                        [F1, F2, F3, F4, F5, F6, F7, F8])

     return [Asia, VisitAsia, Smoking, Tuberculosis, Cancer,
                        Bronchitis, TBorCA, Dyspnea, Xray, F1, F2, F3, F4, F5, F6, F7, F8]

def makeQ3(stu_solution):

     ## E,B,S,w,G example from sample questions
     E = stu_solution.Variable('E', ['e', '-e'])
     B = stu_solution.Variable('B', ['b', '-b'])
     S = stu_solution.Variable('S', ['s', '-s'])
     G = stu_solution.Variable('G', ['g', '-g'])
     W = stu_solution.Variable('W', ['w', '-w'])
     FE = stu_solution.Factor('P(E)', [E])
     FB = stu_solution.Factor('P(B)', [B])
     FS = stu_solution.Factor('P(S|E,B)', [S, E, B])
     FG = stu_solution.Factor('P(G|S)', [G,S])
     FW = stu_solution.Factor('P(W|S)', [W,S])

     FE.add_values([['e',0.1], ['-e', 0.9]])
     FB.add_values([['b', 0.1], ['-b', 0.9]])
     FS.add_values([['s', 'e', 'b', .9], ['s', 'e', '-b', .2], ['s', '-e', 'b', .8],['s', '-e', '-b', 0],
                    ['-s', 'e', 'b', .1], ['-s', 'e', '-b', .8], ['-s', '-e', 'b', .2],['-s', '-e', '-b', 1]])
     FG.add_values([['g', 's', 0.5], ['g', '-s', 0], ['-g', 's', 0.5], ['-g', '-s', 1]])
     FW.add_values([['w', 's', 0.8], ['w', '-s', .2], ['-w', 's', 0.2], ['-w', '-s', 0.8]])

     Q3 = stu_solution.BN('SampleQ4', [E,B,S,G,W], [FE,FB,FS,FG,FW])
     return [Q3,E,B,S,G,W,FE,FB,FS,FG,FW]