# Look for #IMPLEMENT tags in this file.
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
    ##IMPLEMENT
    n = len(futo_grid)
    dom = []
    for i in range(n):
        dom.append(i + 1)
    vars = []
    vararray = []
    for i in dom:
        temp = []
        for j in dom:
            if futo_grid[i - 1][(j - 1) * 2] != 0:
                vars.append(Variable('({},{})'.format(i, j), [futo_grid[i - 1][(j - 1) * 2]]))
                vars[-1].assign(futo_grid[i - 1][(j - 1) * 2])
            else:
                vars.append(Variable('({},{})'.format(i, j), dom))
            temp.append(vars[-1])
        vararray.append(temp)

    cons = []
    nvar = len(vars)
    for i in range(nvar):
        for j in range(i + 1, nvar):
            icoord = (int(vars[i].name[1]), int(vars[i].name[3]))
            jcoord = (int(vars[j].name[1]), int(vars[j].name[3]))

            # check if not on same row or same column
            if icoord[0] != jcoord[0] and icoord[1] != jcoord[1]:
                continue

            con = Constraint("C({},{})".format(icoord, jcoord), [vars[i], vars[j]])

            # creating satisfaction tuples
            sat = []
            # check for inequality if they are next to each other horizontally
            if abs(icoord[1] - jcoord[1]) == 1:
                inequality = futo_grid[icoord[0] - 1][icoord[1] + jcoord[1] - 2]
                if inequality != '.':
                    for val in dom:
                        # check if both variables are assigned
                        if vars[i].is_assigned() and vars[j].is_assigned():
                            sat.append((vars[i].get_assigned_value(), vars[j].get_assigned_value()))
                            break
                        elif vars[i].is_assigned():
                            acheck = "{} {} {}".format(vars[i].get_assigned_value(), inequality, val)
                            if eval(acheck):
                                sat.append((vars[i].get_assigned_value(), val))
                        elif vars[j].is_assigned():
                            bcheck = "{} {} {}".format(val, inequality, vars[j].get_assigned_value())
                            if eval(bcheck):
                                sat.append((k, vars[j].get_assigned_value()))
                        # if neither are assigned
                        else:
                            for num in itertools.permutations(dom, 2):
                                tcheck = "{} {} {}".format(num[0], inequality, num[1])
                                if eval(tcheck):
                                    sat.append(num)
                            break
                else:
                    for val in dom:
                        if vars[i].is_assigned() and vars[j].is_assigned():
                            sat.append((vars[i].get_assigned_value(), vars[j].get_assigned_value()))
                            break
                        elif vars[i].is_assigned():
                            if vars[i].get_assigned_value() != val:
                                sat.append((vars[i].get_assigned_value(), val))
                        elif vars[j].is_assigned():
                            if vars[j].get_assigned_value() != val:
                                sat.append((val, vars[j].get_assigned_value()))
                        else:
                            sat = [_ for _ in itertools.permutations(dom, 2)]
                            break
            # not next to each other horizontally
            else:
                for val in dom:
                    if vars[i].is_assigned() and vars[j].is_assigned():
                        sat.append((vars[i].get_assigned_value(), vars[j].get_assigned_value()))
                        break
                    elif vars[i].is_assigned():
                        if vars[i].get_assigned_value() != val:
                            sat.append((vars[i].get_assigned_value(), val))
                    elif vars[j].is_assigned():
                        if vars[j].get_assigned_value() != val:
                            sat.append((val, vars[j].get_assigned_value()))
                    else:
                        sat = [_ for _ in itertools.permutations(dom, 2)]
                        break
            con.add_satisfying_tuples(sat)
            cons.append(con)
    csp = CSP("Futoshiki Model 1", vars)
    for con in cons:
        csp.add_constraint(con)
    return csp, vararray


def futoshiki_csp_model_2(futo_grid):
    ##IMPLEMENT
    n = len(futo_grid)
    dom = []
    for i in range(n):
        dom.append(i + 1)
    vars = []
    vararray = []
    for i in dom:
        temp = []
        for j in dom:
            if futo_grid[i - 1][(j - 1) * 2] != 0:
                vars.append(Variable('({},{})'.format(i, j), [futo_grid[i - 1][(j - 1) * 2]]))
                vars[-1].assign(futo_grid[i - 1][(j - 1) * 2])
            else:
                vars.append(Variable('({},{})'.format(i, j), dom))
            temp.append(vars[-1])
        vararray.append(temp)

    cons = []
    nvar = len(vars)
    # checking for inequality between 2 cells
    for i in range(nvar):
        for j in range(i + 1, nvar):
            icoord = (int(vars[i].name[1]), int(vars[i].name[3]))
            jcoord = (int(vars[j].name[1]), int(vars[j].name[3]))

            # check if not on same row or same column
            if icoord[0] != jcoord[0]:
                continue

            con = Constraint("C(Inequality {},{})".format(icoord, jcoord), [vars[i], vars[j]])

            # creating satisfaction tuples
            sat = []
            # check for inequality if they are next to each other horizontally
            if abs(icoord[1] - jcoord[1]) == 1:
                inequality = futo_grid[icoord[0] - 1][icoord[1] + jcoord[1] - 2]
                if inequality != '.':
                    for val in dom:
                        # check if both variables are assigned
                        if vars[i].is_assigned() and vars[j].is_assigned():
                            sat.append((vars[i].get_assigned_value(), vars[j].get_assigned_value()))
                            break
                        elif vars[i].is_assigned():
                            acheck = "{} {} {}".format(vars[i].get_assigned_value(), inequality, val)
                            if eval(acheck):
                                sat.append((vars[i].get_assigned_value(), val))
                        elif vars[j].is_assigned():
                            bcheck = "{} {} {}".format(val, inequality, vars[j].get_assigned_value())
                            if eval(bcheck):
                                sat.append((val, vars[j].get_assigned_value()))
                        # if neither are assigned
                        else:
                            for num in itertools.permutations(dom, 2):
                                tcheck = "{} {} {}".format(num[0], inequality, num[1])
                                if eval(tcheck):
                                    sat.append(num)
                            break
                    con.add_satisfying_tuples(sat)
                    cons.append(con)

    # creating column constraints
    for i in range(n):
        colvar = [vararray[j][i] for j in range(n)]
        con = Constraint("C(Column {})".format(i + 1), colvar)
        sat = [_ for _ in itertools.permutations(dom, n)]
        con.add_satisfying_tuples(sat)
        cons.append(con)

    # creating row constraints
    for i in range(n):
        con = Constraint("C(Row {})".format(i + 1), vararray[i])
        sat = [_ for _ in itertools.permutations(dom, n)]
        con.add_satisfying_tuples(sat)
        cons.append(con)

    csp = CSP("Futoshiki Model 2", vars)
    for con in cons:
        csp.add_constraint(con)
    return csp, vararray
