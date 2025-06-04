import pandas as pd
# from bnetbase_solved import *
from carDiagnosis import *
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

#from the worksheet
FB.add_values([
    ['b', 'a', 'h', 1.0], ['b', 'a', '-h', 0.0], ['b', '-a', 'h', 0.5],['b', '-a', '-h', 0.6],
    ['-b', 'a', 'h', 0.0], ['-b', 'a', '-h', 1.0], ['-b', '-a', 'h', 0.5],['-b', '-a', '-h', 0.4]
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
    value = value.lower()
    value = value.strip()
    value = value.replace(" ", "_")
    value = value.replace("'", "")
    if value == "ture":
        value = "true"
    return value

responses = pd.read_csv('csc384_a4_q2.csv', index_col="teach.cs ID")

var_lookup = {"Alternator": al, "Charging system": cs, "Battery age": ba, "Battery voltage": bv, 
                "Main fuse": mf, "Distributer": ds, "Voltage at plug": pv, "Starter motor": sm, 
                "Starter system": ss, "Headlights": hl, "Spark plugs": sp, "Spark quality": sq,
                "Car cranks": cc, "Spark timing": tm, "Fuel system": fs, "Air filter": af,
                "Air system": asys, "Car starts": st}

results = []
for index, row in responses.iterrows():
    current_result = {"teach.cs ID": "", "question 1": 0,
                    "question 2a": 0, "question 2b": 0, "question 2c": 0, "question 2d": 0, "total": 0, 
                    "date submitted": row["Timestamp"]}

    teach_cs_id = index
    print("teach.cs id: {}".format(teach_cs_id), end=" ")
    current_result["teach.cs ID"] = teach_cs_id

    print("1a:", end=" ")
    try:
        # Question 1a
        answer = row['What is P(B=true|A=true)?']
        A.set_evidence('a')
        probs = VE(Q1, B, [A])
        probs_alt = VE(Q1_alternate, B, [A])
        if abs(probs[0]-answer) < 0.001:
            current_result["question 1"] += 2.5
        elif abs(probs_alt[0]-answer) < 0.001:
            current_result["question 1"] += 2.5 
    except Exception as e:
        print("Problem grading Q1a: {}".format(e), end=" ")
    print("1b:", end=" ")
    try:
        # Question 1b
        answer = row['What is P(C=true|A=true)?']
        A.set_evidence('a')
        probs = VE(Q1, C, [A])
        probs_alt = VE(Q1_alternate, C, [A])
        if abs(probs[0]-answer) < 0.001:
            current_result["question 1"] += 2.5
        elif abs(probs_alt[0]-answer) < 0.001:
            current_result["question 1"] += 2.5 
    except Exception as e:
        print("Problem grading Q1b: {}".format(e), end=" ")
    try:
        # Question 1c
        answer = row['What is P(C=true|A=true, E=false)?']
        A.set_evidence('a')
        E.set_evidence('-e')
        probs = VE(Q1, C, [A,E])
        probs_alt = VE(Q1_alternate, C, [A,E])
        if abs(probs[0]-answer) < 0.001:
            current_result["question 1"] += 2.5
        elif abs(probs_alt[0]-answer) < 0.001:
            current_result["question 1"] += 2.5 
    except Exception as e:
        print("Problem grading Q1c: {}".format(e), end=" ")
    try:
        # Question 1d
        answer = row['What is P(C=true|A=true, F=false)?']
        A.set_evidence('a')
        F.set_evidence('-f')
        probs = VE(Q1, C, [A,F])
        probs_alt = VE(Q1_alternate, C, [A,F])
        if abs(probs[0]-answer) < 0.001:
            current_result["question 1"] += 2.5
        elif abs(probs_alt[0]-answer) < 0.001:
            current_result["question 1"] += 2.5 
    except Exception as e:
        print("Problem grading Q1d: {}".format(e), end=" ")
        
    print("2a:", end=" ")
    try:
        # Question 2a
        v1 = var_lookup[row['V1']]
        v2 = var_lookup[row['V2']]
        v3 = var_lookup[row['V3']]
        probs1 = VE(car, v3, [v2, v1])
        probs2 = VE(car, v3, [v1])
        diffs = [abs(probs1[i]-probs2[i]) < 0.001 for i in range(len(probs1))]
        if all(diffs):
            current_result["question 2a"] += 5
    except Exception as e:
        print("Problem grading Q2a: {}".format(e), end=" ")

    print("2b:", end=" ")
    try:
        # Question 2b
        v1 = var_lookup[row['V1.1']]
        v2 = var_lookup[row['V2.1']]
        v3 = var_lookup[row['V3.1']]
        probs_v1 = VE(car, v1, [v2])
        probs_v1_v2 = VE(car, v1, [v2])
        probs_v1_v3 = VE(car, v1, [v3])
        probs_v1_v2_v3 = VE(car, v1, [v2, v3])
        diffs1 = [abs(probs_v1[i]-probs_v1_v2[i]) < 0.001 for i in range(len(probs_v1))]
        diffs2 = [abs(probs_v1_v3[i]-probs_v1_v2_v3[i]) > 0.001 for i in range(len(probs_v1_v3))]
        if all(diffs1) and any(diffs2):
            current_result["question 2b"] += 5
  
    except Exception as e:
        print("Problem grading Q2b: {}".format(e), end=" ")

    # Question 2c
    print("2c:", end=" ")
    v0 = var_lookup[row['V0']]
    d0 = clean_value(row['d0'])
    v1 = var_lookup[row['V1.2']]
    d1 = clean_value(row['d1'])
    v2 = var_lookup[row['V2.2']]
    d2 = clean_value(row['d2'])
    v3 = var_lookup[row['V3.2']]
    d3 = clean_value(row['d3'])
    v4 = var_lookup[row['V4']]
    d4 = clean_value(row['d4'])
    v5 = var_lookup[row['V5']]
    d5 = clean_value(row['d5'])

    prob_answer = float(clean_value(row['What is P(V0=d0|V1=d1,V2=d2,V3=d3,V4=d4,V5=d5)?']))
    
    try:
        query_index = v0.value_index(d0)
        probs0 = VE(car, v0, [])

        v1.set_evidence(d1)
        probs1 = VE(car, v0, [v1])
        diff = probs1[query_index] - probs0[query_index]
        if diff >= 0:
            current_result["question 2c"] += 1.8

        v2.set_evidence(d2)
        probs2 = VE(car, v0, [v1, v2])
        diff = probs2[query_index] - probs1[query_index]
        if diff >= 0:
            current_result["question 2c"] += 1.8

        v3.set_evidence(d3)
        probs3 = VE(car, v0, [v1, v2, v3])
        diff = probs3[query_index] - probs2[query_index]
        if diff >= 0:
            current_result["question 2c"] += 1.8

        v4.set_evidence(d4)
        probs4 = VE(car, v0, [v1, v2, v3, v4])
        diff = probs4[query_index] - probs3[query_index]
        if diff >= 0:
            current_result["question 2c"] += 1.8
      
        v5.set_evidence(d5)
        probs5 = VE(car, v0, [v1, v2, v3, v4, v5])
        diff = probs5[query_index] - probs4[query_index]
        if diff >= 0:
            current_result["question 2c"] += 1.8

        if abs(probs5[query_index]-prob_answer) < 0.001:
            current_result["question 2c"] += 1

    except ValueError as e:
        print("invalid input given: {}".format(e), end=" ")
    except IndexError as e:
        print("problem {}".format(e), end=" ")

    # Question 2d
    print("2d:", end=" ")
    v0 = var_lookup[row['V0.1']]
    d0 = clean_value(row['d0.1'])
    v1 = var_lookup[row['V1.3']]
    d1 = clean_value(row['d1.1'])
    v2 = var_lookup[row['V2.3']]
    d2 = clean_value(row['d2.1'])
    v3 = var_lookup[row['V3.3']]
    d3 = clean_value(row['d3.1'])
    v4 = var_lookup[row['V4.1']]
    d4 = clean_value(row['d4.1'])
    v5 = var_lookup[row['V5.1']]
    d5 = clean_value(row['d5.1'])
    prob_answer = float(clean_value(row['What is P(V0=d0|V1=d1,V2=d2,V3=d3,V4=d4,V5=d5)?.1']))
    try:
        query_index = v0.value_index(d0)
        probs0 = VE(car, v0, [])
        
        v1.set_evidence(d1)
        probs1 = VE(car, v0, [v1])
        diff = probs1[query_index] - probs0[query_index]
        if diff <= 0:
            current_result["question 2d"] += 1.8

        v2.set_evidence(d2)
        probs2 = VE(car, v0, [v1, v2])
        diff = probs2[query_index] - probs1[query_index]
        if diff <= 0:
            current_result["question 2d"] += 1.8
            
        v3.set_evidence(d3)
        probs3 = VE(car, v0, [v1, v2, v3])
        diff = probs3[query_index] - probs2[query_index]
        if diff <= 0:
            current_result["question 2d"] += 1.8
            
        v4.set_evidence(d4)
        probs4 = VE(car, v0, [v1, v2, v3, v4])
        diff = probs4[query_index] - probs3[query_index]
        if diff <= 0:
            current_result["question 2d"] += 1.8
            
        v5.set_evidence(d5)
        probs5 = VE(car, v0, [v1, v2, v3, v4, v5])
        diff = probs5[query_index] - probs4[query_index]
        if diff <= 0:
            current_result["question 2d"] += 1.8

        if abs(probs5[query_index]-prob_answer) < 0.001:
            current_result["question 2d"] += 1
            
    except ValueError as e:
        print("invalid input given: {}".format(e), end=" ")
    except Exception as e:
        print("Problem grading Q2d: {}".format(e), end=" ")

    print("")
    current_result["total"] = (current_result["question 1"] + current_result["question 2a"] + 
                                current_result["question 2b"] + current_result["question 2c"] +
                                current_result["question 2d"])
    results.append(current_result)
results_df = pd.DataFrame(results)

results_df.to_csv("csc384_a4_response_grades.csv", index=False)