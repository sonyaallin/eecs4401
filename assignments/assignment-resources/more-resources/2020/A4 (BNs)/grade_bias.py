import pandas as pd
# from bnetbase_solved import *
from medicalDiagnosis import *
import math

A = Variable('A', ['a', '-a'])
B = Variable('B', ['b', '-b'])
C = Variable('C', ['c', '-c'])
D = Variable('D', ['d', '-d'])
E = Variable('E', ['e', '-e'])
F = Variable('F', ['f', '-f'])
G = Variable('G', ['g', '-g'])
H = Variable('H', ['h', '-h'])
I = Variable('I', ['i', '-i'])

FA = Factor('P(A)', [A])
FF = Factor('P(F)', [F])
FG = Factor('P(G)', [G])
FH = Factor('P(H)', [H])

FB = Factor('P(B|A,H)', [B,A,H])
FC = Factor('P(C|B,G)', [C,B,G])
FD = Factor('P(D|C,F)', [D,C,F])
FE = Factor('P(E|C)', [E,C])
FI = Factor('P(I|B)', [I,B])

FI_alt = Factor('P(I|B)', [I,B])
FB_alt = Factor('P(B|A,H)', [B,A,H])

FA.add_values([['a',0.9], ['-a', 0.1]])
FF.add_values([['f', 0.1], ['-f', 0.9]])
FG.add_values([['g', 1.0], ['-g', 0.0]])
FH.add_values([['h', 0.5], ['-h', 0.5]])

FB.add_values([
    ['b', 'a', 'h', 1.0], ['b', 'a', '-h', 0.0], ['b', '-a', 'h', 0.5],['b', '-a', '-h', 0.6],
    ['-b', 'a', 'h', 0.0], ['-b', 'a', '-h', 1.0], ['-b', '-a', 'h', 0.5],['-b', '-a', '-h', 0.4]
    ])

FC.add_values([
    ['c', 'b', 'g', 0.9], ['c', '-b', 'g', 0.1], ['c', 'b', '-g', 0.9], ['c', '-b', '-g', 1.0],
    ['-c', 'b', 'g', 0.1], ['-c', '-b', 'g', 0.9], ['-c', 'b', '-g', 0.1], ['-c', '-b', '-g', 0.0]
    ])
FD.add_values([
    ['d', 'c', 'f', 0.0], ['d', '-c', 'f', 0.7], ['d', 'c', '-f', 1.0], ['d', '-c', '-f', 0.2],
    ['-d', 'c', 'f', 1.0], ['-d', '-c', 'f', 0.3], ['-d', 'c', '-f', 0.0], ['-d', '-c', '-f', 0.8]
    ])
FE.add_values([
    ['e', 'c', 0.2], ['e', '-c', 0.4], ['-e', 'c', 0.8], ['-e', '-c', 0.6]
])
FI.add_values([
    ['i', 'b', 0.3], ['i', '-b', 0.9], ['-i', 'b', 0.7], ['-i', '-b', 0.1]
])

FB_alt.add_values([
    ['b', 'a', 'h', 1.0], ['b', 'a', '-h', 0.0], ['b', '-a', 'h', 0.0],['b', '-a', '-h', 0.6],
    ['-b', 'a', 'h', 0.0], ['-b', 'a', '-h', 1.0], ['-b', '-a', 'h', 1.0],['-b', '-a', '-h', 0.4]
    ])
FI_alt.add_values([
    ['i', 'b', 1.0], ['i', '-b', 0.0], ['-i', 'b', 0.7], ['-i', '-b', 0.1]
])

Q1 = BN('Q1', [A,B,C,D,E,F,G,H,I], [FA,FB,FC,FD,FE,FF,FG,FH,FI])

Q1_alternate = BN('Q1_alternate', [A,B,C,D,E,F,G,H,I], [FA,FB_alt,FC,FD,FE,FF,FG,FH,FI_alt])

def clean_value(value):
    value = str(value)
    #value = value.lower()
    value = value.strip()
    value = value.replace(" ", "_")
    value = value.replace("'", "")
    if value == "ture":
        value = "true"
    return value

#responses = pd.read_csv('csc384_a4_q2.csv', index_col="id")

var_lookup = {"BMI": bmi, "Central_Obesity": co, "Hypertension": ht, "Hyperlipidemia": hl, 
                "Vegetables": vg, "Gender": gd, "Region": rg, "Diabetes": db, 
                "Age": ag, "Activity": ac}

var1 = hl;
var2 = gd;
var3 = co;

var1 = hl;
var2 = gd;
var3 = rg;

var1 = co;
var2 = gd;
var3 = hl;

domains1 = var1.domain()
domains2 = var2.domain()
domains3 = var3.domain()

#separated
print("Separated")
for a in domains1:
    for b in domains2:
        var1.set_evidence(a)
        var2.set_evidence(b)
        q1 = VE(medical, var3, [var1])
        q2 = VE(medical, var3, [var1, var2])

        for i in [0,1]:
            print(round(q1[i],3),round(q2[i],3),round(q1[i],3)==round(q2[i],3))


#sufficient
print("Sufficient")
for a in domains3:
    for b in domains2:
        var3.set_evidence(a)
        var2.set_evidence(b)
        q1 = VE(medical, var1, [var3])
        q2 = VE(medical, var1, [var3, var2])

        for i in [0,1]:
            print(round(q1[i],3),round(q2[i],3),round(q1[i],3)==round(q2[i],3))


P_ACY = [[1, 1, 1, 0.15], 
[1, 0, 1, 0.15],
[1, 1, 0, 0.05],
[1, 0, 0, 0.15], 
[0, 1, 1, 0.1],
[0, 0, 1, 0.1],  
[0, 1, 0, 0.1],
[0, 0, 0, 0.2]]

P_AY = [[1,1,0],
[1,0,0],
[0,1,0],
[0,0,0]
]

P_CY = [[1,1,0],
[1,0,0],
[0,1,0],
[0,0,0]
]

P_Y = [[1,0],
[0,0]
]

#P(C|YA) = P(C|Y)    
#P(CYA)/P(YA) = P(CY)/P(Y)
for row in P_ACY:
    if (row[2] == 1): #Y is 1
        P_Y[0][1] += row[3]
        if (row[1] == 1): #C is 1
            P_CY[0][2] += row[3]  
        elif (row[1] == 0): #C is 0
            P_CY[2][2] += row[3]   
        if (row[0] == 1): #A is 1
            P_AY[0][2] += row[3]  
        elif (row[0] == 0):
            P_AY[2][2] += row[3]              
    else:
        P_Y[1][1] += row[3] 
        if (row[1] == 1): #C is 1
            P_CY[1][2] += row[3]  
        elif (row[1] == 0): #C is 0
            P_CY[3][2] += row[3]  
        if (row[0] == 1): 
            P_AY[1][2] += row[3]  
        elif (row[0] == 0):
            P_AY[3][2] += row[3]   

#P(C|YA)
P_CgivenAY = [[1, 0, 1, 0], 
[1, 1, 1, 0],
[1, 1, 0, 0],
[1, 0, 0, 0], 
[0, 0, 1, 0],
[0, 1, 1, 0],  
[0, 1, 0, 0],
[0, 0, 0, 0]]

print(P_AY[0][2])
print(P_ACY[0][3])
print(P_ACY[1][3])
input()
print(P_AY[1][2])
print(P_ACY[2][3])
print(P_ACY[3][3])
input()
print(P_AY[2][2])
print(P_ACY[4][3])
print(P_ACY[5][3])
input()
print(P_AY[3][2])
print(P_ACY[6][3])
print(P_ACY[7][3])
input()

P_CgivenAY[0][3] = P_ACY[0][3]/P_AY[0][2]
P_CgivenAY[1][3] = P_ACY[1][3]/P_AY[0][2]
P_CgivenAY[2][3] = P_ACY[2][3]/P_AY[1][2]
P_CgivenAY[3][3] = P_ACY[3][3]/P_AY[1][2]
P_CgivenAY[4][3] = P_ACY[4][3]/P_AY[2][2]
P_CgivenAY[5][3] = P_ACY[5][3]/P_AY[2][2]
P_CgivenAY[6][3] = P_ACY[6][3]/P_AY[3][2]
P_CgivenAY[7][3] = P_ACY[7][3]/P_AY[3][2]

P_CgivenY = [[1,1,0],
[1,0,0],
[0,1,0],
[0,0,0]
]

P_CgivenY[0][2] = P_CY[0][2]/P_Y[0][1]
P_CgivenY[1][2] = P_CY[1][2]/P_Y[1][1]
P_CgivenY[2][2] = P_CY[2][2]/P_Y[0][1]
P_CgivenY[3][2] = P_CY[3][2]/P_Y[1][1]

print("\n")
print(P_Y[0])
print(P_Y[1])
print("\n")
print(P_AY[0])
print(P_AY[1])
print(P_AY[2])
print(P_AY[3])
print("\n")
print(P_CY[0])
print(P_CY[1])
print(P_CY[2])
print(P_CY[3])
print("\n")
print(P_CgivenAY[0])
print(P_CgivenAY[1])
print(P_CgivenAY[2])
print(P_CgivenAY[3])
print(P_CgivenAY[4])
print(P_CgivenAY[5])
print(P_CgivenAY[6])
print(P_CgivenAY[7])
print("\n")
print(P_CgivenY[0])
print(P_CgivenY[1])
print(P_CgivenY[2])
print(P_CgivenY[3])
