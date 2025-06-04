#Look for #IMPLEMENT tags in this file.

'''
Construct and return funpuzz CSP models.
'''
import itertools

from cspbase import *

def binary_ne_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only binary all-different
    constraints for both the row and column constraints.

    Returns a CSP object representing a FunPuzz Grid CSP problem along with an array of variables
    for the problem. That is return:

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using binary constraints
    to enforce row and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """
    domain = [i for i in range(1, funpuzz_grid[0][0]+1)]
    variables = []
    constr = []
    for i in domain:
        row = []
        for j in domain:
            row.append(Variable(f"Var{i}{j}", domain))
        variables.append(row)

    for i in domain:
        for j in domain:
            for k in domain:
                if not k > j:
                    continue
                v1, v2 = variables[i-1][j-1], variables[i-1][k-1]
                row_con = Constraint(f"C(V{i}{j},V{i}{k})", [v1, v2])
                sat_tuples = []
                for pair in itertools.product(v1.domain(), v2.domain()):
                    if pair[0] != pair[1]:
                        sat_tuples.append(pair)
                row_con.add_satisfying_tuples(sat_tuples)
                constr.append(row_con)
            for k in domain:
                if not k > i:
                    continue
                v1, v2 = variables[i-1][j-1], variables[k-1][j-1]
                col_con = Constraint(f"C(V{i}{j},V{k}{j})", [v1, v2])
                sat_tuples = []
                for pair in itertools.product(v1.domain(), v2.domain()):
                    if pair[0] != pair[1]:
                        sat_tuples.append(pair)
                col_con.add_satisfying_tuples(sat_tuples)
                constr.append(col_con)

    flattened_vars = list(itertools.chain.from_iterable(variables))
    funpuzz_csp = CSP("binary", flattened_vars)
    for c in constr:
        funpuzz_csp.add_constraint(c)

    return funpuzz_csp, variables


def nary_ad_grid(funpuzz_grid):
    """A model of a funpuzz grid (without cage constraints) built using only n-ary all-different
    constraints for both the row and column constraints.
    
    Returns a CSP object representing a Cageoky Grid CSP problem along with an array of variables
    for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using n-ary constraints to enforce row
    and column constraints and variable_array is a list of lists:

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does not require implementation of cage constraints.
    """
    def duplicates(lst):
        seen = []
        for item in lst:
            if item in seen:
                return True
            else:
                seen.append(item)
        return False

    domain = [i for i in range(1, funpuzz_grid[0][0] + 1)]
    variables = []
    constr = []
    for i in domain:
        row = []
        for j in domain:
            row.append(Variable(f"Var{i}{j}", domain))
        variables.append(row)

    for i in domain:
        row_vars = []
        col_vars = []
        row_name = ""
        col_name = ""
        for j in domain:
            row_vars += [variables[i-1][j-1]]
            col_vars += [variables[j-1][i-1]]
            if row_name == "":
                row_name += f"V{i}{j}"
            else:
                row_name += f",V{i}{j}"
            if col_name == "":
                col_name += f"V{j}{i}"
            else:
                col_name += f",V{j}{i}"

        row_con = Constraint(f"C({row_name})", row_vars)
        sat_tuples = []
        for nlist in itertools.product(*[v.domain() for v in row_vars]):
            if not duplicates(nlist):
                sat_tuples.append(nlist)

        row_con.add_satisfying_tuples(sat_tuples)

        col_con = Constraint(f"C({col_name})", col_vars)
        sat_tuples = []
        for nlist in itertools.product(*[v.domain() for v in col_vars]):
            if not duplicates(nlist):
                sat_tuples.append(nlist)
        col_con.add_satisfying_tuples(sat_tuples)

        constr.extend([row_con, col_con])

    flattened_vars = list(itertools.chain.from_iterable(vars))
    funpuzz_csp = CSP("n-ary", flattened_vars)
    for c in constr:
        funpuzz_csp.add_constraint(c)

    return funpuzz_csp, vars


def funpuzz_csp_model(funpuzz_grid):
    """A model built using your choice of (1) binary binary not-equal, or (2) n-ary all-different
    constraints for the grid, together with (3) funpuzz cage constraints. That is, you will
    choose one of the previous two grid models and expand it to include cage constraints
    for the funpuzz Variation.

    Returns a CSP object representing a Cageoky Grid CSP problem along with an array of variables
    for the problem. That is return

       funpuzz_csp, variable_array

    where funpuzz_csp is a csp representing funpuzz grid using constraints
    to enforce cage, row and column constraints and variable_array is a list of lists

       [ [  ]
         [  ]
         .
         .
         .
         [  ] ]

    such that variable_array[i][j] is the Variable (object) that you built to represent the value
    to be placed in cell i,j of the funpuzz Grid.

    Note that this model does require implementation of cage constraints.
    """
    domain = [i for i in range(1, funpuzz_grid[0][0] + 1)]
    vars = []
    constr = []
    for i in domain:
        row = []
        for j in domain:
            row.append(Variable(f"Var{i}{j}", domain))
        vars.append(row)

    # cage constraints
    for cage in funpuzz_grid[1:]:
        if len(cage) == 2:
            cell_name = cage[0]
            target = cage[1]
            i = int(str(cell_name[0]))
            j = int(str(cell_name[1]))
            vars[i-1][j-1] = Variable(f"V{i}{j}", [target])
        else:
            target = cage[-2]
            op = cage[-1]
            cells = cage[:-2]
            constr_vars = []
            constr_var_names = ""
            cage_domain = []
            for cell in cells:
                cell_name = str(cell)
                i, j = int(cell_name[0]), int(cell_name[1])
                constr_vars += [vars[i-1][j-1]]
                cage_domain += [vars[i-1][j-1].domain()]
                if constr_var_names == "":
                    constr_var_names += f"V{i}{j}"
                else:
                    constr_var_names += f",V{i}{j}"

            cage_con = Constraint(f"C({constr_var_names})", constr_vars)
            sat_tuples = []
            for nlist in itertools.product(*cage_domain):
                if op == 0:
                    # addition
                    if sum(nlist) == target:
                        sat_tuples.append(nlist)
                elif op == 1:
                    # subtraction
                    for perm in itertools.permutations(nlist):
                        diff = perm[0]
                        for n in perm[1:]:
                            diff -= n
                        if diff == target:
                            sat_tuples.append(nlist)
                elif op == 2:
                    # division
                    for perm in itertools.permutations(nlist):
                        diff = perm[0]
                        for n in perm[1:]:
                            diff /= n
                        if diff == target:
                            sat_tuples.append(nlist)
                elif op == 3:
                    # multiplication
                    product = 1
                    for n in nlist:
                        product *= n
                    if product == target:
                        sat_tuples.append(nlist)

            cage_con.add_satisfying_tuples(sat_tuples)
            constr.append(cage_con)

    # bin-ary constraints
    for i in domain:
        for j in domain:
            for k in domain:
                if k <= j:
                    continue
                var1 = vars[i - 1][j - 1]
                var2 = vars[i - 1][k - 1]
                row_con = Constraint(f"C(V{i}{j},V{i}{k})", [var1, var2])
                sat_tuples = []
                for pair in itertools.product(var1.domain(), var2.domain()):
                    if pair[0] != pair[1]:
                        sat_tuples.append(pair)
                row_con.add_satisfying_tuples(sat_tuples)
                constr.append(row_con)
            for k in domain:
                if k <= i:
                    continue
                var1 = vars[i - 1][j - 1]
                var2 = vars[k - 1][j - 1]
                col_con = Constraint(f"C(V{i}{j},V{k}{j})", [var1, var2])
                sat_tuples = []
                for pair in itertools.product(var1.domain(), var2.domain()):
                    if pair[0] != pair[1]:
                        sat_tuples.append(pair)
                col_con.add_satisfying_tuples(sat_tuples)
                constr.append(col_con)

    flattened_vars = list(itertools.chain.from_iterable(vars))
    funpuzz_csp = CSP("caged binary", flattened_vars)
    for c in constr:
        funpuzz_csp.add_constraint(c)

    return funpuzz_csp, vars
