#Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary
      all-different constraints for both the row and column constraints.

'''
from cspbase import *
import itertools

def futoshiki_csp_model_1(futo_grid):
    i = 0
    dom = []
    for i in range(len(futo_grid)):
        dom.append(i+1)
    vars = []
    cons = []
    operations = []
    for qi in range(len(futo_grid)):
        row_vars_index = 0
        inside_var = []
        inside_operations = []
        for qj in range(len(futo_grid[qi])):
            if type(futo_grid[qi][qj]) == int:
                if futo_grid[qi][qj] !=0:
                    var = Variable("V{}{}".format(qi,row_vars_index), [futo_grid[qi][qj]])
                    var.assign(futo_grid[qi][qj])
                    inside_var.append(var)
                else:
                    inside_var.append(Variable("V{}{}".format(qi,row_vars_index), dom))
                row_vars_index += 1
            if type(futo_grid[qi][qj]) == str:
                inside_operations.append(futo_grid[qi][qj])
        operations.append(inside_operations)
        vars.append(inside_var)

    for qi in range(len(vars)):
        row_operation_index = 0
        for qj in range(len(vars[qi])-1): # qi, qj -> 1,2,3 in domain and qk, qj -> 2,3,4
            for qk in range(qj+1, len(vars)):
                con = Constraint("C(V{}{},V{}{})".format(qi,qj,qi,qk), [vars[qi][qj], vars[qi][qk]])
                tuples = []
                if operations[qi][qj] == '>' and qk == qj+1:
                    for number1, number2 in itertools.product(vars[qi][qj].cur_domain(), vars[qi][qk].cur_domain()):
                        if number1 > number2:
                            tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                if operations[qi][qj] == '<' and qk == qj+1:
                    for number1, number2 in itertools.product(vars[qi][qj].cur_domain(), vars[qi][qk].cur_domain()):
                        if number1 < number2:
                            tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                if operations[qi][qj] == '.' or qk != qj+1:
                    for number1, number2 in itertools.product(vars[qi][qj].cur_domain(), vars[qi][qk].cur_domain()):
                        if number1 != number2:
                            tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                cons.append(con)

    for qi in range(len(vars)):
        row_operation_index = 0
        for qj in range(len(vars[qi])-1): # qi, qj -> 1,2,3 in domain and qk, qj -> 2,3,4
            for qk in range(qj+1, len(vars)):
                con = Constraint("C(V{}{},V{}{})".format(qj,qi,qk,qi), [vars[qj][qi], vars[qk][qi]])
                tuples = []
                if operations[qi][qj] == '>':
                    for number1, number2 in itertools.product(vars[qj][qi].cur_domain(), vars[qk][qi].cur_domain()):
                        if number1 > number2:
                            tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                if operations[qi][qj] == '<':
                    for number1, number2 in itertools.product(vars[qj][qi].cur_domain(), vars[qk][qi].cur_domain()):
                        if number1 < number2:
                            tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                if operations[qi][qj] == '.':
                    for number1, number2 in itertools.product(vars[qj][qi].cur_domain(), vars[qk][qi].cur_domain()):
                        if number1 != number2:
                            tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                cons.append(con)

    vars2= [var for row in vars for var in row]
    csp = CSP("futoshiki", vars2)
    for c in cons:
        csp.add_constraint(c)
    return csp, vars

def helper(tup: tuple):
    if len(tup) == len(set(tup)):
        return True
    return False


def futoshiki_csp_model_2(futo_grid):
    i = 0
    dom = []
    for i in range(len(futo_grid)):
        dom.append(i+1)
    vars = []
    cons = []
    operations = []
    for qi in range(len(futo_grid)):
        row_vars_index = 0
        inside_var = []
        inside_operations = []
        for qj in range(len(futo_grid[qi])):
            if type(futo_grid[qi][qj]) == int:
                if futo_grid[qi][qj] !=0:
                    var = Variable("V{}{}".format(qi,row_vars_index), [futo_grid[qi][qj]])
                    var.assign(futo_grid[qi][qj])
                    inside_var.append(var)
                else:
                    inside_var.append(Variable("V{}{}".format(qi,row_vars_index), dom))
                row_vars_index += 1
            if type(futo_grid[qi][qj]) == str:
                inside_operations.append(futo_grid[qi][qj])
        operations.append(inside_operations)
        vars.append(inside_var)

    for qi in range(len(vars)):
        col = []
        row = vars[qi]
        domain_row = []
        domain_col = []
        tuples_row = []
        tuples_col = []
        for qj in range(len(vars[qi])):
            col.append(vars[qj][qi])
            domain_row.append(vars[qi][qj].cur_domain())
            domain_col.append(vars[qj][qi].cur_domain())
        con = Constraint("row {} constraint".format(qi), row)
        con_col=Constraint("col {} constraint".format(qi),col)
        for i in itertools.product(*domain_row):
            if helper(i):
                tuples_row.append(i)
        con.add_satisfying_tuples(tuples_row)
        cons.append(con)
        for i in itertools.product(*domain_col):
            if helper(i):
                tuples_col.append(i)
        con_col.add_satisfying_tuples(tuples_col)
        cons.append(con_col)

    for qi in range(len(vars)):
        for qj in range(len(vars[qi])-1):
            if 1:
                if operations[qi][qj] != "." :
                    con = Constraint("C(V{}{},V{}{})".format(qi,qj,qi,qj+1), [vars[qi][qj], vars[qi][qj+1]])
                    tuples = []
                    if operations[qi][qj] == '>':
                        for number1, number2 in itertools.product(vars[qi][qj].cur_domain(), vars[qi][qj+1].cur_domain()):
                            if number1 > number2:
                                tuples.append((number1, number2))
                    elif operations[qi][qj] == '<':
                        for number1, number2 in itertools.product(vars[qi][qj].cur_domain(), vars[qi][qj+1].cur_domain()):
                            if number1 < number2:
                                tuples.append((number1, number2))
                    con.add_satisfying_tuples(tuples)
                    cons.append(con)
    vars2= [var for row in vars for var in row]
    csp = CSP("futoshiki", vars2)
    for c in cons:
        csp.add_constraint(c)
    return csp, vars
